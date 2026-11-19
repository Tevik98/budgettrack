// Applies expense filters as soon as a value changes. Without JavaScript the
// form still works through its "Apply filters" button.
(function () {
  var form = document.querySelector('form[data-auto-submit]');
  if (!form) return;

  var button = form.querySelector('[data-auto-submit-button]');
  if (button) button.hidden = true;

  // Put keyboard focus back on the filter the person just changed.
  var focusKey = 'budgettrack:filter-focus';
  try {
    var focusId = sessionStorage.getItem(focusKey);
    sessionStorage.removeItem(focusKey);
    var focusField = focusId && document.getElementById(focusId);
    if (focusField) focusField.focus({ preventScroll: true });
  } catch (error) { /* storage unavailable: skip focus restore */ }

  var timer;
  function submit(field) {
    try { sessionStorage.setItem(focusKey, field.id); } catch (error) { /* ignore */ }
    if (form.requestSubmit) form.requestSubmit(); else form.submit();
  }

  form.addEventListener('change', function (event) {
    var field = event.target;
    clearTimeout(timer);
    if (field.type === 'month') {
      // Wait for a pause so typing a month digit by digit doesn't reload the
      // page midway, and ignore half-entered dates.
      if (field.validity && field.validity.badInput) return;
      timer = setTimeout(function () { submit(field); }, 600);
    } else {
      submit(field);
    }
  });
})();
