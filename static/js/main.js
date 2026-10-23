/* Supplyhive — interactive behaviour for the stationery shop layout. */
(function () {
  "use strict";

  /* ----------------------------------------------- mobile navigation ---- */
  var toggle = document.getElementById("navToggle");
  var links = document.getElementById("primaryNav");

  if (toggle && links) {
    toggle.addEventListener("click", function () {
      var open = links.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", String(open));
      toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    });
  }

  /* ------------------------------------------ category sidebar toggle ---- */
  var catToggle = document.getElementById("catToggle");
  var catPanel = document.getElementById("catPanel");

  if (catToggle && catPanel) {
    catToggle.addEventListener("click", function () {
      var open = catPanel.classList.toggle("is-open");
      catToggle.setAttribute("aria-expanded", String(open));
    });
  }

  /* --------------------------------- cart quantity: submit on change ---- */
  document.querySelectorAll(".js-qty-input").forEach(function (input) {
    input.addEventListener("change", function () {
      if (input.form) {
        input.form.submit();
      }
    });
  });

  /* ------------------------- add to cart without leaving the page ------- */
  document.querySelectorAll(".card__form").forEach(function (form) {
    form.addEventListener("submit", function (event) {
      if (!window.fetch) {
        return; // let the plain form post handle it
      }
      event.preventDefault();
      var button = form.querySelector("button");
      var original = button.textContent;

      fetch(form.action, {
        method: "POST",
        body: new FormData(form),
        headers: { "X-Requested-With": "XMLHttpRequest" },
        credentials: "same-origin"
      })
        .then(function (response) {
          if (!response.ok) {
            throw new Error("Request failed");
          }
          return response.json();
        })
        .then(function (payload) {
          updateBadge(payload.count);
          button.textContent = "Added ✓";
          window.setTimeout(function () {
            button.textContent = original;
          }, 1400);
        })
        .catch(function () {
          form.submit();
        });
    });
  });

  function updateBadge(count) {
    var cartLink = document.querySelector('.nav__icon[aria-label="Cart"]');
    if (!cartLink) {
      return;
    }
    var badge = cartLink.querySelector(".nav__badge");
    if (!badge) {
      badge = document.createElement("span");
      badge.className = "nav__badge";
      cartLink.appendChild(badge);
    }
    badge.textContent = count;
  }

  /* -------------------------------- sign in / register tab switcher ---- */
  var authCard = document.getElementById("authCard");

  if (authCard) {
    var tabs = authCard.querySelectorAll(".auth-tabs__tab");
    var panels = authCard.querySelectorAll("form[data-mode]");

    var showMode = function (mode) {
      tabs.forEach(function (tab) {
        var active = tab.getAttribute("data-mode") === mode;
        tab.classList.toggle("is-active", active);
        tab.setAttribute("aria-selected", String(active));
      });
      panels.forEach(function (panel) {
        panel.hidden = panel.getAttribute("data-mode") !== mode;
      });
    };

    // without JavaScript the tabs are plain links that reload with ?mode=...
    tabs.forEach(function (tab) {
      tab.addEventListener("click", function (event) {
        event.preventDefault();
        showMode(tab.getAttribute("data-mode"));
      });
    });

    /* ------------------------------------ show / hide password ---- */
    authCard.querySelectorAll(".js-password-toggle").forEach(function (button) {
      var input = button.parentNode.querySelector("input");
      button.hidden = false; // hidden by default so no-JS visitors never see a dead button
      button.addEventListener("click", function () {
        var show = input.type === "password";
        input.type = show ? "text" : "password";
        button.textContent = show ? "Hide" : "Show";
        button.setAttribute("aria-label", show ? "Hide password" : "Show password");
      });
    });
  }

  /* ----------------------------- phone numbers: digits only, max 10 ---- */
  document.querySelectorAll('input[type="tel"]').forEach(function (input) {
    input.addEventListener("input", function () {
      input.value = input.value.replace(/\D/g, "").slice(0, 10);
    });
  });

  /* ------------------------------------------------- payment page ---- */
  var payCard = document.getElementById("payCard");

  if (payCard) {
    var payTabs = payCard.querySelectorAll(".auth-tabs__tab");
    var payPanels = payCard.querySelectorAll("form[data-mode]");

    payTabs.forEach(function (tab) {
      tab.addEventListener("click", function (event) {
        event.preventDefault();
        var mode = tab.getAttribute("data-mode");
        payTabs.forEach(function (other) {
          var active = other === tab;
          other.classList.toggle("is-active", active);
          other.setAttribute("aria-selected", String(active));
        });
        payPanels.forEach(function (panel) {
          panel.hidden = panel.getAttribute("data-mode") !== mode;
        });
      });
    });

    var numberInput = document.getElementById("id_card_number");
    var expiryInput = document.getElementById("id_expiry");
    var cvvInput = document.getElementById("id_cvv");
    var brandLabel = document.getElementById("cardBrand");

    var detectBrand = function (digits) {
      if (/^3[47]/.test(digits)) { return "American Express"; }
      if (/^(5[1-5]|2[2-7])/.test(digits)) { return "Mastercard"; }
      if (/^(60|65|81|82|508)/.test(digits)) { return "RuPay"; }
      if (/^4/.test(digits)) { return "Visa"; }
      return "";
    };

    var expiryOk = function (value) {
      var m = /^(\d{2})\/(\d{2})$/.exec(value);
      if (!m) { return false; }
      var month = parseInt(m[1], 10);
      var year = 2000 + parseInt(m[2], 10);
      var now = new Date();
      if (month < 1 || month > 12) { return false; }
      return year * 12 + month >= now.getFullYear() * 12 + now.getMonth() + 1 && year <= now.getFullYear() + 20;
    };

    if (numberInput) {
      numberInput.addEventListener("input", function () {
        var digits = numberInput.value.replace(/\D/g, "").slice(0, 19);
        var brand = detectBrand(digits);
        var groups = brand === "American Express" ? [4, 6, 5] : [4, 4, 4, 4, 3];
        var parts = [];
        var pos = 0;
        groups.forEach(function (size) {
          if (digits.length > pos) { parts.push(digits.substr(pos, size)); }
          pos += size;
        });
        numberInput.value = parts.join(" ");
        if (brandLabel) { brandLabel.textContent = brand; }
        var expected = brand === "American Express" ? 15 : 16;
        numberInput.setCustomValidity(digits.length > 0 && digits.length !== expected ? "Enter a valid card number (" + expected + " digits)." : "");
      });
    }

    if (expiryInput) {
      expiryInput.addEventListener("input", function () {
        var digits = expiryInput.value.replace(/\D/g, "").slice(0, 4);
        if (digits.length > 2) { digits = digits.slice(0, 2) + "/" + digits.slice(2); }
        expiryInput.value = digits;
        expiryInput.setCustomValidity(digits.length === 5 && !expiryOk(digits) ? "This card has expired or the date is invalid." : "");
      });
    }

    if (cvvInput) {
      cvvInput.addEventListener("input", function () {
        cvvInput.value = cvvInput.value.replace(/\D/g, "").slice(0, 3);
      });
    }
  }

  /* ----------------------------- price filter: apply on change ---- */
  document.querySelectorAll(".js-price-filter").forEach(function (form) {
    var apply = form.querySelector(".js-filter-apply");
    if (apply) {
      apply.hidden = true; // without JavaScript the Apply button stays visible
    }
    form.addEventListener("change", function () {
      form.submit();
    });
  });

  /* --------------------------------- dismiss flash messages on click ---- */
  document.querySelectorAll(".flash").forEach(function (flash) {
    window.setTimeout(function () {
      flash.style.transition = "opacity .4s ease";
      flash.style.opacity = "0";
      window.setTimeout(function () {
        flash.remove();
      }, 400);
    }, 4000);
  });
})();
