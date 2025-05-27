function disableSubmit(form) {
  const btn = form.querySelector("button[type='submit']");
  if (btn) {
    btn.disabled = true;
    btn.innerText = "Submitting...";
  }
}

function enableSubmit(form) {
  const btn = form.querySelector("button[type='submit']");
  if (btn) {
    btn.disabled = false;
    btn.innerText = "Submit Request";
  }
}

function resetForm(form) {
  const successAlert = form
    .closest("#leave-form-container")
    .querySelector(".alert-success");
  if (successAlert) {
    form.reset();
  }
}
