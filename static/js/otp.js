// =========================
// ELEMENT REFERENCES
// =========================

var stepPhone = document.getElementById('step-phone');
var stepOtp = document.getElementById('step-otp');
var stepSuccess = document.getElementById('step-success');

var countryCodeSelect = document.getElementById('country-code');
var phoneInput = document.getElementById('phone');
var phoneStatus = document.getElementById('phone-status');

var sendOtpBtn = document.getElementById('send-otp-btn');
var sentPhoneLabel = document.getElementById('sent-phone');

var otpCodeInput = document.getElementById('otp-code');
var otpStatus = document.getElementById('otp-status');

var verifyBtn = document.getElementById('verify-btn');
var resendBtn = document.getElementById('resend-btn');
var otpTimer = document.getElementById('otp-timer');

var otpFallbackCodeEl = document.getElementById('otp-fallback-code');
var otpFallbackCodeValueEl = document.getElementById('otp-fallback-code-value');

var otpTimerInterval = null;
var currentPhone = '';

// Registration context
var isRegistration = document.getElementById('otp-is-register');
var prefillPhone = document.getElementById('otp-phone');
var isRegistering = isRegistration && isRegistration.value === '1';

// Forgot password context
var isForgotEl = document.getElementById('otp-is-forgot');
var isForgotPassword = isForgotEl && isForgotEl.value === '1';

// =========================
// INITIALIZATION
// =========================

(function init() {
    // Update UI for registration context
    if (isRegistering) {
        var titleEl = document.getElementById('otp-title');
        var subtitleEl = document.getElementById('otp-subtitle');
        if (titleEl) titleEl.textContent = 'Verify Your Phone';
        if (subtitleEl) subtitleEl.textContent = 'We need to verify your phone before creating your account';

        // Pre-fill phone number if provided
        if (prefillPhone && prefillPhone.value) {
            var fullPhone = prefillPhone.value;
            // Parse country code and local number
            var countryCode = '+254';
            var localNumber = fullPhone;

            // Try to detect country code
            for (var i = 0; i < countryCodeSelect.options.length; i++) {
                var opt = countryCodeSelect.options[i].value;
                if (fullPhone.startsWith(opt)) {
                    countryCode = opt;
                    localNumber = fullPhone.substring(opt.length);
                    break;
                }
            }

            countryCodeSelect.value = countryCode;
            phoneInput.value = localNumber;
            currentPhone = fullPhone;

            // Auto-send OTP
            setTimeout(function () {
                sendOtpBtn.click();
            }, 500);
        }
    }

    // Update UI for forgot password context
    if (isForgotPassword) {
        var titleEl = document.getElementById('otp-title');
        var subtitleEl = document.getElementById('otp-subtitle');
        if (titleEl) titleEl.textContent = 'Reset Password';
        if (subtitleEl) subtitleEl.textContent = 'Verify your phone number to reset your password';

        // Pre-fill phone number if provided
        if (prefillPhone && prefillPhone.value) {
            var fullPhone = prefillPhone.value;
            var countryCode = '+254';
            var localNumber = fullPhone;

            for (var i = 0; i < countryCodeSelect.options.length; i++) {
                var opt = countryCodeSelect.options[i].value;
                if (fullPhone.startsWith(opt)) {
                    countryCode = opt;
                    localNumber = fullPhone.substring(opt.length);
                    break;
                }
            }

            countryCodeSelect.value = countryCode;
            phoneInput.value = localNumber;
            currentPhone = fullPhone;

            // Auto-send OTP
            setTimeout(function () {
                sendOtpBtn.click();
            }, 500);
        }
    }
})();

// =========================
// SEND OTP
// =========================

if (sendOtpBtn) {
    sendOtpBtn.addEventListener('click', function () {
        var countryCode = countryCodeSelect.value;
        var phone = phoneInput.value.trim();

        // Validate phone number
        if (!phone) {
            phoneStatus.className = 'field-status error';
            phoneStatus.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Phone number is required';
            phoneInput.focus();
            return;
        }

        if (phone.length < 7) {
            phoneStatus.className = 'field-status error';
            phoneStatus.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Please enter a valid phone number';
            phoneInput.focus();
            return;
        }

        // Build full phone number
        currentPhone = countryCode + phone.replace(/^\+/, '');

        // Disable button and show loading
        sendOtpBtn.disabled = true;
        sendOtpBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';

        fetch('/api/send-otp', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone: currentPhone })
        })
        .then(function (response) { return response.json(); })
        .then(function (data) {
            if (data.success) {
                if (data.otpFallback) {
                    // SMS failed but OTP code is available — show it on screen
                    otpFallbackCode = data.otpCode; // Store for timer
                    phoneStatus.className = 'field-status warning';
                    phoneStatus.innerHTML = '<i class="fas fa-exclamation-triangle"></i> SMS not available. Your OTP code is: <strong>' + data.otpCode + '</strong>';

                    // Transition to step 2 after a longer delay so the user can read the code
                    setTimeout(function () {
                        stepPhone.style.display = 'none';
                        stepOtp.style.display = 'block';
                        sentPhoneLabel.textContent = data.phone || currentPhone;

                        // Show the OTP code prominently in the dedicated display area
                        if (otpFallbackCodeValueEl) {
                            otpFallbackCodeValueEl.textContent = data.otpCode;
                        }
                        if (otpFallbackCodeEl) {
                            otpFallbackCodeEl.style.display = 'block';
                        }

                        // Auto-fill the OTP code
                        otpCodeInput.value = data.otpCode;
                        otpCodeInput.focus();

                        // Start countdown timer (5 minutes) - timer will show the OTP code
                        startOtpTimer(300);
                    }, 2000);
                } else if (data.otpSent === false) {
                    // WhatsApp delivery failed — warn user but still proceed to OTP step
                    phoneStatus.className = 'field-status error';
                    phoneStatus.innerHTML = '<i class="fas fa-exclamation-triangle"></i> ' + (data.message || 'WhatsApp delivery failed. The phone may not be on WhatsApp, or the free trial rate limit (1 message/min) has been reached. You can retry on the next page.');

                    // Transition to step 2 after a longer delay so the user can read the warning
                    setTimeout(function () {
                        stepPhone.style.display = 'none';
                        stepOtp.style.display = 'block';
                        sentPhoneLabel.textContent = data.phone || currentPhone;
                        otpCodeInput.focus();

                        // Show a warning in the OTP step about rate limiting
                        if (otpTimer) {
                            otpTimer.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Free trial: wait 60 seconds before retrying.';
                        }
                        // Start a 60-second cooldown before allowing resend
                        startOtpTimer(60);
                    }, 1500);
                } else {
                    // Show success message
                    phoneStatus.className = 'field-status success';
                    phoneStatus.innerHTML = '<i class="fas fa-check-circle"></i> OTP sent to ' + (data.phone || currentPhone);

                    // Transition to step 2
                    setTimeout(function () {
                        stepPhone.style.display = 'none';
                        stepOtp.style.display = 'block';
                        sentPhoneLabel.textContent = data.phone || currentPhone;
                        otpCodeInput.focus();

                        // Start countdown timer (5 minutes)
                        startOtpTimer(300);
                    }, 800);
                }

            } else {
                sendOtpBtn.disabled = false;
                sendOtpBtn.innerHTML = '<i class="fab fa-whatsapp"></i> Send OTP via WhatsApp';
                phoneStatus.className = 'field-status error';
                phoneStatus.innerHTML = '<i class="fas fa-exclamation-triangle"></i> ' + (data.message || 'Failed to send OTP');
            }
        })
        .catch(function () {
            sendOtpBtn.disabled = false;
            sendOtpBtn.innerHTML = '<i class="fab fa-whatsapp"></i> Send OTP via WhatsApp';
            phoneStatus.className = 'field-status error';
            phoneStatus.innerHTML = '<i class="fas fa-times-circle"></i> Network error. Please try again.';
        });
    });
}

// =========================
// VERIFY OTP
// =========================

if (verifyBtn) {
    verifyBtn.addEventListener('click', function () {
        var code = otpCodeInput.value.trim();

        if (!currentPhone) {
            otpStatus.className = 'field-status error';
            otpStatus.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Phone number is required';
            return;
        }

        if (!code || code.length !== 6) {
            otpStatus.className = 'field-status error';
            otpStatus.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Please enter the 6-digit code';
            otpCodeInput.focus();
            return;
        }

        // Disable button and show loading
        verifyBtn.disabled = true;
        verifyBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Verifying...';

        fetch('/api/verify-otp', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone: currentPhone, otp_code: code })
        })
        .then(function (response) { return response.json(); })
        .then(function (data) {
            if (data.success) {
                // OTP verified successfully
                otpStatus.className = 'field-status success';
                otpStatus.innerHTML = '<i class="fas fa-check-circle"></i> Phone verified successfully!';

                // Stop timer
                stopOtpTimer();

                // Transition to next step
                setTimeout(function () {
                    stepOtp.style.display = 'none';

                    // If in forgot password mode, show reset password step
                    if (isForgotPassword) {
                        var stepReset = document.getElementById('step-reset');
                        if (stepReset) {
                            stepReset.style.display = 'block';
                            var newPassInput = document.getElementById('new-password');
                            if (newPassInput) newPassInput.focus();
                        }
                    } else {
                        // Otherwise show success step
                        stepSuccess.style.display = 'block';

                        // If in registration mode, complete registration
                        if (isRegistering) {
                            var successTitle = document.getElementById('success-title');
                            var successMsg = document.getElementById('success-message');
                            var registeringBox = document.getElementById('registering-box');
                            var continueBtn = document.getElementById('continue-btn');

                            if (successTitle) successTitle.textContent = 'Phone Verified!';
                            if (successMsg) successMsg.textContent = 'Creating your account...';
                            if (registeringBox) registeringBox.style.display = 'block';
                            if (continueBtn) continueBtn.style.display = 'none';

                            // Get stored form data from sessionStorage
                            var pendingData = sessionStorage.getItem('pending_registration');
                            if (pendingData) {
                                var formData = JSON.parse(pendingData);
                                fetch('/api/complete-registration', {
                                    method: 'POST',
                                    headers: { 'Content-Type': 'application/json' },
                                    body: JSON.stringify(formData)
                                })
                                .then(function (resp) { return resp.json(); })
                                .then(function (result) {
                                    if (result.success) {
                                        if (successMsg) successMsg.textContent = 'Account created successfully! Redirecting...';
                                        if (registeringBox) registeringBox.style.display = 'none';
                                        sessionStorage.removeItem('pending_registration');
                                        setTimeout(function () {
                                            window.location.href = result.redirect || '/profile';
                                        }, 1500);
                                    } else {
                                        if (successMsg) successMsg.textContent = 'Verification complete but registration failed: ' + (result.message || 'Unknown error');
                                        if (registeringBox) registeringBox.style.display = 'none';
                                        if (continueBtn) {
                                            continueBtn.style.display = 'inline-flex';
                                            continueBtn.href = '/';
                                        }
                                    }
                                })
                                .catch(function () {
                                    if (successMsg) successMsg.textContent = 'Verification complete but network error during registration';
                                    if (registeringBox) registeringBox.style.display = 'none';
                                    if (continueBtn) {
                                        continueBtn.style.display = 'inline-flex';
                                        continueBtn.href = '/';
                                    }
                                });
                            } else {
                                // No pending data, just show success
                                if (successMsg) successMsg.textContent = 'Your phone number has been verified successfully.';
                                if (registeringBox) registeringBox.style.display = 'none';
                                if (continueBtn) {
                                    continueBtn.style.display = 'inline-flex';
                                    continueBtn.href = '/';
                                }
                            }
                        }
                    }
                }, 1000);

            } else {
                verifyBtn.disabled = false;
                verifyBtn.innerHTML = '<i class="fas fa-check"></i> Verify Code';
                otpStatus.className = 'field-status error';
                otpStatus.innerHTML = '<i class="fas fa-exclamation-triangle"></i> ' + (data.message || 'Invalid OTP code');
                otpCodeInput.value = '';
                otpCodeInput.focus();
            }
        })
        .catch(function () {
            verifyBtn.disabled = false;
            verifyBtn.innerHTML = '<i class="fas fa-check"></i> Verify Code';
            otpStatus.className = 'field-status error';
            otpStatus.innerHTML = '<i class="fas fa-times-circle"></i> Network error. Please try again.';
        });
    });
}

// =========================
// RESEND OTP
// =========================

if (resendBtn) {
    resendBtn.addEventListener('click', function () {
        resendBtn.disabled = true;
        resendBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Resending...';

        fetch('/api/send-otp', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone: currentPhone })
        })
        .then(function (response) { return response.json(); })
        .then(function (data) {
            if (data.success) {
                if (data.otpFallback) {
                    // SMS failed but OTP code is available — show it on screen
                    otpFallbackCode = data.otpCode;
                    otpStatus.className = 'field-status warning';
                    otpStatus.innerHTML = '<i class="fas fa-exclamation-triangle"></i> SMS not available. Your OTP code is: <strong>' + data.otpCode + '</strong>';
                    // Show the OTP code prominently
                    if (otpFallbackCodeValueEl) {
                        otpFallbackCodeValueEl.textContent = data.otpCode;
                    }
                    if (otpFallbackCodeEl) {
                        otpFallbackCodeEl.style.display = 'block';
                    }
                    // Auto-fill the OTP code
                    otpCodeInput.value = data.otpCode;
                    resendBtn.disabled = false;
                    resendBtn.innerHTML = '<i class="fas fa-redo"></i> Resend Code';
                    // Restart timer - will show the OTP code
                    startOtpTimer(300);
                } else if (data.otpSent === false) {
                    // WhatsApp delivery failed on resend — warn about rate limit
                    otpStatus.className = 'field-status error';
                    otpStatus.innerHTML = '<i class="fas fa-exclamation-triangle"></i> ' + (data.message || 'WhatsApp delivery failed. Free trial limit: 1 message per minute. Please wait before retrying.');
                    resendBtn.disabled = false;
                    resendBtn.innerHTML = '<i class="fas fa-redo"></i> Resend Code';
                    // Start a 60-second cooldown
                    startOtpTimer(60);
                } else {
                    otpStatus.className = 'field-status success';
                    otpStatus.innerHTML = '<i class="fas fa-check-circle"></i> New OTP sent!';
                    resendBtn.style.display = 'none';

                    // Restart timer
                    startOtpTimer(300);
                }
            } else {
                resendBtn.disabled = false;
                resendBtn.innerHTML = '<i class="fas fa-redo"></i> Resend Code';
                otpStatus.className = 'field-status error';
                otpStatus.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Failed to resend OTP';
            }
        })
        .catch(function () {
            resendBtn.disabled = false;
            resendBtn.innerHTML = '<i class="fas fa-redo"></i> Resend Code';
            otpStatus.className = 'field-status error';
            otpStatus.innerHTML = '<i class="fas fa-times-circle"></i> Network error. Please try again.';
        });
    });
}

// =========================
// OTP COUNTDOWN TIMER
// =========================

function startOtpTimer(seconds) {
    stopOtpTimer();
    var remaining = seconds;

    function updateTimer() {
        var minutes = Math.floor(remaining / 60);
        var secs = remaining % 60;
        var timeStr = minutes.toString().padStart(2, '0') + ':' + secs.toString().padStart(2, '0');

        if (otpTimer) {
            otpTimer.innerHTML = '<i class="fas fa-clock"></i> Resend in ' + timeStr;
        }

        if (remaining <= 0) {
            stopOtpTimer();
            if (otpTimer) {
                otpTimer.innerHTML = '';
            }
            // Show resend button
            if (resendBtn) {
                resendBtn.style.display = 'flex';
                resendBtn.disabled = false;
                resendBtn.innerHTML = '<i class="fas fa-redo"></i> Resend Code';
            }
        } else {
            remaining--;
        }
    }

    updateTimer();
    otpTimerInterval = setInterval(updateTimer, 1000);
}

function stopOtpTimer() {
    if (otpTimerInterval) {
        clearInterval(otpTimerInterval);
        otpTimerInterval = null;
    }
}

// =========================
// INPUT VALIDATION
// =========================

// Allow only numeric input for OTP
if (otpCodeInput) {
    otpCodeInput.addEventListener('input', function () {
        this.value = this.value.replace(/[^0-9]/g, '');
    });
}

// Allow only numeric input for phone
if (phoneInput) {
    phoneInput.addEventListener('input', function () {
        this.value = this.value.replace(/[^0-9\s]/g, '');
    });
}

// Clear phone status on input
if (phoneInput) {
    phoneInput.addEventListener('input', function () {
        if (phoneStatus) {
            phoneStatus.className = 'field-status';
            phoneStatus.innerHTML = '';
        }
    });
}

// Clear OTP status on input
if (otpCodeInput) {
    otpCodeInput.addEventListener('input', function () {
        if (otpStatus) {
            otpStatus.className = 'field-status';
            otpStatus.innerHTML = '';
        }
    });
}

// =========================
// ENTER KEY SUPPORT
// =========================

// Press Enter in phone input to send OTP
if (phoneInput) {
    phoneInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            sendOtpBtn.click();
        }
    });
}

// Press Enter in OTP input to verify
if (otpCodeInput) {
    otpCodeInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            verifyBtn.click();
        }
    });
}

// =========================
// RESET PASSWORD (Forgot Password Flow)
// =========================

var resetPasswordBtn = document.getElementById('reset-password-btn');
var newPasswordInput = document.getElementById('new-password');
var confirmPasswordInput = document.getElementById('confirm-password');
var resetStatus = document.getElementById('reset-status');

// Toggle new password visibility
var toggleNewPassword = document.getElementById('toggle-new-password');
if (toggleNewPassword && newPasswordInput) {
    toggleNewPassword.addEventListener('click', function () {
        var icon = this.querySelector('i');
        if (newPasswordInput.type === 'password') {
            newPasswordInput.type = 'text';
            icon.classList.remove('fa-eye');
            icon.classList.add('fa-eye-slash');
        } else {
            newPasswordInput.type = 'password';
            icon.classList.remove('fa-eye-slash');
            icon.classList.add('fa-eye');
        }
    });
}

// Toggle confirm password visibility
var toggleConfirmPassword = document.getElementById('toggle-confirm-password');
if (toggleConfirmPassword && confirmPasswordInput) {
    toggleConfirmPassword.addEventListener('click', function () {
        var icon = this.querySelector('i');
        if (confirmPasswordInput.type === 'password') {
            confirmPasswordInput.type = 'text';
            icon.classList.remove('fa-eye');
            icon.classList.add('fa-eye-slash');
        } else {
            confirmPasswordInput.type = 'password';
            icon.classList.remove('fa-eye-slash');
            icon.classList.add('fa-eye');
        }
    });
}

// Reset password button click
if (resetPasswordBtn) {
    resetPasswordBtn.addEventListener('click', function () {
        var newPass = newPasswordInput.value;
        var confirmPass = confirmPasswordInput.value;

        // Validate inputs
        if (!newPass || !confirmPass) {
            if (resetStatus) {
                resetStatus.className = 'field-status error';
                resetStatus.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Please fill in both password fields';
            }
            return;
        }

        if (newPass.length < 6) {
            if (resetStatus) {
                resetStatus.className = 'field-status error';
                resetStatus.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Password must be at least 6 characters';
            }
            return;
        }

        if (newPass !== confirmPass) {
            if (resetStatus) {
                resetStatus.className = 'field-status error';
                resetStatus.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Passwords do not match';
            }
            return;
        }

        // Disable button and show loading
        resetPasswordBtn.disabled = true;
        resetPasswordBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Resetting...';

        fetch('/api/reset-password', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                phone: currentPhone,
                new_password: newPass,
                confirm_password: confirmPass
            })
        })
        .then(function (response) { return response.json(); })
        .then(function (data) {
            if (data.success) {
                if (resetStatus) {
                    resetStatus.className = 'field-status success';
                    resetStatus.innerHTML = '<i class="fas fa-check-circle"></i> Password reset successfully! Redirecting...';
                }
                resetPasswordBtn.disabled = true;
                resetPasswordBtn.innerHTML = '<i class="fas fa-check"></i> Done';

                // Redirect to login page after 2 seconds
                setTimeout(function () {
                    window.location.href = '/account/logi';
                }, 2000);
            } else {
                resetPasswordBtn.disabled = false;
                resetPasswordBtn.innerHTML = '<i class="fas fa-save"></i> Reset Password';
                if (resetStatus) {
                    resetStatus.className = 'field-status error';
                    resetStatus.innerHTML = '<i class="fas fa-exclamation-triangle"></i> ' + (data.message || 'Failed to reset password');
                }
            }
        })
        .catch(function () {
            resetPasswordBtn.disabled = false;
            resetPasswordBtn.innerHTML = '<i class="fas fa-save"></i> Reset Password';
            if (resetStatus) {
                resetStatus.className = 'field-status error';
                resetStatus.innerHTML = '<i class="fas fa-times-circle"></i> Network error. Please try again.';
            }
        });
    });
}

// Allow Enter key to submit reset password
if (confirmPasswordInput) {
    confirmPasswordInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            resetPasswordBtn.click();
        }
    });
}

// Clear reset status on input
if (newPasswordInput) {
    newPasswordInput.addEventListener('input', function () {
        if (resetStatus) {
            resetStatus.className = 'field-status';
            resetStatus.innerHTML = '';
        }
    });
}

if (confirmPasswordInput) {
    confirmPasswordInput.addEventListener('input', function () {
        if (resetStatus) {
            resetStatus.className = 'field-status';
            resetStatus.innerHTML = '';
        }
    });
}
