// =========================
// PHONE AUTO-FORMAT TO +254
// =========================

(function () {
    var phoneInput = document.getElementById('phone');
    var countryCodeSelect = document.getElementById('country-code');

    if (phoneInput) {
        phoneInput.addEventListener('input', function () {
            // Strip non-numeric characters
            var val = this.value.replace(/[^0-9]/g, '');

            // Auto-format to +2547XXXXXXXX pattern
            if (val.length > 0) {
                // If starts with 0, remove leading zero
                if (val.charAt(0) === '0') {
                    val = val.substring(1);
                }
                // If starts with 254, remove country code prefix (user will use country code dropdown)
                if (val.startsWith('254')) {
                    val = val.substring(3);
                }
                // Ensure starts with 7 for Kenyan numbers
                if (val.length > 0 && val.charAt(0) !== '7') {
                    // Keep as-is for non-Kenyan, but for +254 selected, ensure 7
                    if (countryCodeSelect && countryCodeSelect.value === '+254' && val.charAt(0) !== '7') {
                        // Auto-prepend 7 if user typed something else
                        val = '7' + val;
                    }
                }
            }

            this.value = val;
        });

        // On blur, validate format for +254
        phoneInput.addEventListener('blur', function () {
            var val = this.value.replace(/[^0-9]/g, '');
            var statusEl = document.getElementById('phone-status');

            if (countryCodeSelect && countryCodeSelect.value === '+254') {
                // Kenyan format: should be 7XXXXXXXX (9 digits)
                if (val.length > 0 && val.charAt(0) !== '7') {
                    val = '7' + val;
                    this.value = val;
                }
                if (val.length === 9 && val.charAt(0) === '7') {
                    if (statusEl) {
                        statusEl.className = 'field-status success';
                        statusEl.innerHTML = '<i class="fas fa-check-circle"></i> Valid Kenyan number: +' + countryCodeSelect.value.replace('+', '') + val;
                    }
                } else if (val.length > 0 && val.length < 9) {
                    if (statusEl) {
                        statusEl.className = 'field-status error';
                        statusEl.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Kenyan number should be 9 digits starting with 7 (e.g., 712345678)';
                    }
                }
            }
        });
    }
})();

// =========================
// INTERCEPT FORM SUBMISSION FOR OTP
// =========================

(function () {
    var profileForm = document.querySelector('.profile-form');
    if (!profileForm) return;

    profileForm.addEventListener('submit', function (e) {
        e.preventDefault();

        var submitBtn = document.getElementById('submit-btn');
        var phoneInput = document.getElementById('phone');
        var countryCodeSelect = document.getElementById('country-code');

        // Build full phone number
        var phone = phoneInput ? phoneInput.value.trim() : '';
        var countryCode = countryCodeSelect ? countryCodeSelect.value : '+254';

        // Auto-format phone for +254
        if (countryCode === '+254') {
            phone = phone.replace(/[^0-9]/g, '');
            if (phone.length > 0 && phone.charAt(0) === '0') {
                phone = phone.substring(1);
            }
            if (phone.length > 0 && phone.charAt(0) !== '7') {
                phone = '7' + phone;
            }
        }

        var fullPhone = countryCode + phone;

        // Validate phone
        if (!phone || phone.length < 9) {
            var phoneStatus = document.getElementById('phone-status');
            if (phoneStatus) {
                phoneStatus.className = 'field-status error';
                phoneStatus.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Please enter a valid phone number';
            } else {
                alert('Please enter a valid phone number');
            }
            return;
        }

        // Disable submit button
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Verifying Phone...';
        }

        // Collect form data
        var formData = new FormData(profileForm);
        var formDataObj = {};
        formData.forEach(function (value, key) {
            if (key !== 'profile_picture') {
                formDataObj[key] = value;
            }
        });

        // Store form data in sessionStorage
        formDataObj._phone = fullPhone;
        formDataObj._action = profileForm.action || window.location.pathname;
        sessionStorage.setItem('pending_registration', JSON.stringify(formDataObj));

        // Send OTP via API
        fetch('/api/prepare-otp', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone: fullPhone })
        })
        .then(function (response) { return response.json(); })
        .then(function (data) {
            if (data.success) {
                // Redirect to OTP page
                window.location.href = '/otp?phone=' + encodeURIComponent(fullPhone) + '&register=1';
            } else {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = '<i class="fas fa-user-plus"></i> Create Account';
                }
                alert(data.message || 'Failed to send verification code');
            }
        })
        .catch(function () {
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="fas fa-user-plus"></i> Create Account';
            }
            alert('Network error. Please try again.');
        });
    });
})();
