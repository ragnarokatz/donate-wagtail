import client from "braintree-web/client";
import hostedFields from "braintree-web/hosted-fields";

function setupBraintree() {
  var paymentForm = document.getElementById("payments__braintree-form"),
    nonceInput = document.getElementById("id_braintree_nonce"),
    paymentModeInput = document.getElementById("id_payment_mode"),
    submitButton = document.getElementById("payments__payment-submit"),
    token = paymentForm.getAttribute("data-token"),
    loadingErrorMsg =
      "An error occurred. Please reload the page or try again later.",
    paymentAmount = paymentForm.getAttribute("data-amount"),
    paymentCurrency = "USD",
    errorDiv = document.getElementById("payments__braintree-errors-card"),
    braintreeErrorClass = "braintree-hosted-fields-invalid",
    braintreeParams = JSON.parse(
      document.getElementById("payments__braintree-params").textContent
    );

  function showErrorMessage(msg) {
    errorDiv.toggleAttribute("hidden", false);
    errorDiv.innerHTML = msg;
  }

  function clearErrorMessage() {
    errorDiv.toggleAttribute("hidden", true);
    errorDiv.innerHTML = "";
  }

  function showFieldError(container) {
    container.classList.add(braintreeErrorClass);
  }

  function clearFieldError(container) {
    container.classList.remove(braintreeErrorClass);
  }

  function initHostedFields() {
    client.create({ authorization: token }, function(
      clientErr,
      clientInstance
    ) {
      if (clientErr) {
        showErrorMessage(loadingErrorMsg);
        return;
      }

      var options = {
        client: clientInstance,
        styles: {},
        fields: {
          number: {
            selector: "#card-number"
          },
          cvv: {
            selector: "#cvv"
          },
          expirationDate: {
            selector: "#expiration-date"
          }
        }
      };

      hostedFields.create(options, function(
        hostedFieldsErr,
        hostedFieldsInstance
      ) {
        if (hostedFieldsErr) {
          showErrorMessage(loadingErrorMsg);
          cardInputDiv.toggleAttribute("hidden", true);
          return;
        }

        submitButton.removeAttribute("disabled");

        hostedFieldsInstance.on("validityChange", function(event) {
          var field = event.fields[event.emittedBy];

          if (field.isValid || field.isPotentiallyValid) {
            clearFieldError(field.container);
          } else {
            showFieldError(field.container);
          }
        });

        submitButton.addEventListener("click", function(e) {
          e.preventDefault();
          var state = hostedFieldsInstance.getState(),
            formValid = Object.keys(state.fields).every(function(key) {
              var isValid = state.fields[key].isValid;
              if (!isValid) {
                showFieldError(state.fields[key].container);
              }
              return isValid;
            });

          if (formValid) {
            clearErrorMessage("card");
            hostedFieldsInstance.tokenize(function(tokenizeErr, payload) {
              if (tokenizeErr) {
                showErrorMessage(
                  "There was an error processing your payment. Please try again."
                );
                return;
              }

              nonceInput.value = payload.nonce;
              paymentModeInput.value = "card";
              paymentForm.submit();
            });
          } else {
            showErrorMessage(
              "Some of the fields below are invalid. Please correct the invalid fields and try again."
            );
          }
        });
      });
    });
  }

  initHostedFields();
}

document.addEventListener("DOMContentLoaded", function() {
  setupBraintree();
});
