// =========================
// PROFILE PICTURE PREVIEW
// =========================

var pictureInput = document.getElementById('profile-picture');
var picturePreview = document.getElementById('picture-preview');

if (pictureInput && picturePreview) {
    pictureInput.addEventListener('change', function (e) {
        var file = e.target.files[0];
        if (file) {
            var reader = new FileReader();
            reader.onload = function (event) {
                picturePreview.style.backgroundImage = 'url(' + event.target.result + ')';
                picturePreview.innerHTML = '';
            };
            reader.readAsDataURL(file);
        }
    });
}

// =========================
// TOGGLE PASSWORD VISIBILITY
// =========================

var toggleBtn = document.getElementById('toggle-password');
var passwordInput = document.getElementById('password');

if (toggleBtn && passwordInput) {
    toggleBtn.addEventListener('click', function () {
        var icon = this.querySelector('i');
        if (passwordInput.type === 'password') {
            passwordInput.type = 'text';
            icon.classList.remove('fa-eye');
            icon.classList.add('fa-eye-slash');
        } else {
            passwordInput.type = 'password';
            icon.classList.remove('fa-eye-slash');
            icon.classList.add('fa-eye');
        }
    });
}

// =========================
// TOGGLE CONFIRM PASSWORD VISIBILITY
// =========================

var toggleConfirmBtn = document.getElementById('toggle-confirm-password');
var confirmPasswordInput = document.getElementById('confirm-password');

if (toggleConfirmBtn && confirmPasswordInput) {
    toggleConfirmBtn.addEventListener('click', function () {
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

// =========================
// USERNAME VALIDATION
// =========================

var usernameInput = document.getElementById('username');
var usernameStatus = document.getElementById('username-status');
var usernameCheckTimeout = null;

if (usernameInput) {
    usernameInput.addEventListener('input', function () {
        var value = this.value.trim();

        // Clear previous timeout for debouncing
        if (usernameCheckTimeout) {
            clearTimeout(usernameCheckTimeout);
        }

        // If field is empty, clear status
        if (!value) {
            usernameStatus.className = 'field-status';
            usernameStatus.innerHTML = '';
            usernameInput.classList.remove('field-success', 'field-error');
            return;
        }

        // Show checking state
        usernameStatus.className = 'field-status checking';
        usernameStatus.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Checking...';
        usernameInput.classList.remove('field-success', 'field-error');

        // Debounce: wait 500ms before making the API call
        usernameCheckTimeout = setTimeout(function () {
            fetch('/api/check-username', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username: value })
            })
            .then(function (response) { return response.json(); })
            .then(function (data) {
                if (data.available) {
                    // Username is available
                    usernameStatus.className = 'field-status success';
                    usernameStatus.innerHTML = '<i class="fas fa-check-circle"></i> Username is available';
                    usernameInput.classList.add('field-success');
                    usernameInput.classList.remove('field-error');
                } else {
                    // Username already exists
                    usernameStatus.className = 'field-status error';
                    usernameStatus.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Username already exists';
                    usernameInput.classList.add('field-error');
                    usernameInput.classList.remove('field-success');
                }
            })
            .catch(function () {
                usernameStatus.className = 'field-status error';
                usernameStatus.innerHTML = '<i class="fas fa-times-circle"></i> Could not check username';
            });
        }, 500);
    });
}

// =========================
// EMAIL VALIDATION
// =========================

var emailInput = document.getElementById('email');
var emailStatus = document.getElementById('email-status');
var emailCheckTimeout = null;

if (emailInput) {
    emailInput.addEventListener('input', function () {
        var value = this.value.trim();

        // Clear previous timeout for debouncing
        if (emailCheckTimeout) {
            clearTimeout(emailCheckTimeout);
        }

        // If field is empty, clear status
        if (!value) {
            emailStatus.className = 'field-status';
            emailStatus.innerHTML = '';
            emailInput.classList.remove('field-success', 'field-error');
            return;
        }

        // Basic email format check
        var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            emailStatus.className = 'field-status error';
            emailStatus.innerHTML = '<i class="fas fa-times-circle"></i> Please enter a valid email';
            emailInput.classList.add('field-error');
            emailInput.classList.remove('field-success');
            return;
        }

        // Show checking state
        emailStatus.className = 'field-status checking';
        emailStatus.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Checking...';
        emailInput.classList.remove('field-success', 'field-error');

        // Debounce: wait 500ms before making the API call
        emailCheckTimeout = setTimeout(function () {
            fetch('/api/check-email', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: value })
            })
            .then(function (response) { return response.json(); })
            .then(function (data) {
                if (data.available) {
                    // Email is available
                    emailStatus.className = 'field-status success';
                    emailStatus.innerHTML = '<i class="fas fa-check-circle"></i> Email is available';
                    emailInput.classList.add('field-success');
                    emailInput.classList.remove('field-error');
                } else {
                    // Email already registered — redirect to login
                    emailStatus.className = 'field-status error';
                    emailStatus.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Email already registered';
                    emailInput.classList.add('field-error');
                    emailInput.classList.remove('field-success');

                    // Redirect to login page after a short delay
                    setTimeout(function () {
                        if (data.redirect) {
                            window.location.href = data.redirect;
                        } else {
                            window.location.href = '/account/logi';
                        }
                    }, 1500);
                }
            })
            .catch(function () {
                emailStatus.className = 'field-status error';
                emailStatus.innerHTML = '<i class="fas fa-times-circle"></i> Could not check email';
            });
        }, 500);
    });
}

// =========================
// CONFIRM PASSWORD VALIDATION
// =========================

var passwordMatchStatus = document.getElementById('password-match-status');

function checkPasswordMatch() {
    var password = passwordInput.value;
    var confirmPassword = confirmPasswordInput.value;

    if (!confirmPassword) {
        // Empty confirm password — show no status
        passwordMatchStatus.className = 'password-match-status';
        passwordMatchStatus.innerHTML = '';
        confirmPasswordInput.classList.remove('password-match', 'password-mismatch');
        return;
    }

    if (password === confirmPassword) {
        // Passwords match
        passwordMatchStatus.className = 'password-match-status match';
        passwordMatchStatus.innerHTML = '<i class="fas fa-check-circle"></i> Passwords match';
        confirmPasswordInput.classList.add('password-match');
        confirmPasswordInput.classList.remove('password-mismatch');
    } else {
        // Passwords do not match
        passwordMatchStatus.className = 'password-match-status mismatch';
        passwordMatchStatus.innerHTML = '<i class="fas fa-times-circle"></i> Passwords do not match';
        confirmPasswordInput.classList.add('password-mismatch');
        confirmPasswordInput.classList.remove('password-match');
    }
}

if (confirmPasswordInput) {
    // Check on every keystroke
    confirmPasswordInput.addEventListener('input', checkPasswordMatch);
    // Check on blur for immediate feedback
    confirmPasswordInput.addEventListener('blur', checkPasswordMatch);
}

if (passwordInput) {
    // Re-check confirm password when password field changes
    passwordInput.addEventListener('input', function () {
        if (confirmPasswordInput && confirmPasswordInput.value) {
            checkPasswordMatch();
        }
    });
}

// =========================
// LOCATION AUTO-FILL
// =========================

var locationInput = document.getElementById('location');
var locationSwitch = document.getElementById('location-switch');
var gpsBtn = document.getElementById('gps-btn');

if (locationSwitch) {
    locationSwitch.addEventListener('change', function () {
        if (this.checked) {
            autoDetectLocation();
        } else {
            locationInput.value = '';
            locationInput.placeholder = 'Enter your location';
        }
    });
}

if (gpsBtn) {
    gpsBtn.addEventListener('click', function () {
        autoDetectLocation();
    });
}

function autoDetectLocation() {
    if (!navigator.geolocation) {
        alert('Geolocation is not supported by your browser.');
        if (locationSwitch) locationSwitch.checked = false;
        return;
    }

    locationInput.placeholder = 'Detecting location...';
    gpsBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

    navigator.geolocation.getCurrentPosition(
        function (position) {
            var lat = position.coords.latitude;
            var lon = position.coords.longitude;
            fetch('https://nominatim.openstreetmap.org/reverse?format=json&lat=' + lat + '&lon=' + lon + '&zoom=10&addressdetails=1')
                .then(function (response) { return response.json(); })
                .then(function (data) {
                    if (data && data.address) {
                        var address = data.address;
                        var town = address.village || address.town || address.city || address.municipality || address.suburb || '';
                        var county = address.county || address.state_district || address.state || '';

                        if (county && town) {
                            locationInput.value = county + ', ' + town;
                        } else if (town) {
                            locationInput.value = town;
                        } else if (county) {
                            locationInput.value = county;
                        } else {
                            locationInput.value = address.city || address.town || address.village || '';
                        }
                        locationInput.placeholder = 'Location auto-filled';
                    } else {
                        locationInput.placeholder = 'Could not detect location';
                    }
                    gpsBtn.innerHTML = '<i class="fas fa-location-crosshairs"></i>';
                })
                .catch(function () {
                    locationInput.placeholder = 'Error detecting location';
                    gpsBtn.innerHTML = '<i class="fas fa-location-crosshairs"></i>';
                });
        },
        function (error) {
            locationInput.placeholder = 'Location access denied';
            gpsBtn.innerHTML = '<i class="fas fa-location-crosshairs"></i>';
            if (locationSwitch) locationSwitch.checked = false;

            if (error.code === 1) {
                alert('Location access was denied. Please enable location permissions.');
            } else if (error.code === 2) {
                alert('Location is unavailable.');
            } else if (error.code === 3) {
                alert('Location request timed out.');
            }
        },
        {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 0
        }
    );
}

// =========================
// EQUIPMENT CHECKBOX TOGGLE
// =========================

// Track controller selection state for USB monitoring
var controllerSelected = false;
var controllerDetected = false;
var controllerPollInterval = null;

// Track MIDI access and detection state
var midiAccess = null;
var midiDevicesDetected = [];
var midiState = null;

var equipChecks = document.querySelectorAll('.equip-check');

equipChecks.forEach(function (checkbox) {
    checkbox.addEventListener('change', function () {
        // Prevent unchecking PC/Laptop — it is required for DJ registration
        if (this.name === 'equipment_pc' && !this.checked) {
            this.checked = true;
            var statusEl = document.getElementById('pc-status');
            if (statusEl) {
                statusEl.className = 'verification-status failed';
                statusEl.innerHTML = '<i class="fas fa-exclamation-triangle"></i> PC/Laptop is required for DJ registration';
            }
            alert('PC/Laptop is required for DJ registration. It cannot be unchecked.');
            return;
        }

        var equipmentItem = this.closest('.equipment-item');
        var detailsId = '';

        // Determine the details div ID based on the checkbox name
        var name = this.name;
        if (name) {
            var detailMap = {
                'equipment_pc': 'pc-details',
                'equipment_controller': 'controller-details',
                'equipment_mixer': 'mixer-details',
                'equipment_speakers': 'speakers-details',
                'equipment_generator': 'generator-details',
                'equipment_projector': 'projector-details',
                'equipment_microphones': 'microphones-details',
                'equipment_instruments': 'instruments-details'
            };
            detailsId = detailMap[name] || '';
        }

        if (this.checked) {
            equipmentItem.classList.add('active');

            // Auto-detect hardware when checkbox is selected
            if (name === 'equipment_pc') {
                detectPCModel();
            } else if (name === 'equipment_controller') {
                controllerSelected = true;
                controllerDetected = false;
                detectController(); // This function handles MIDI first, then falls back to USB
                // Start polling for controller in case USB connect event is not supported
                startControllerPolling();
            } else if (name === 'equipment_projector') {
                detectProjector();
            }
        } else {
            equipmentItem.classList.remove('active');

            // Clear auto-detected values when unchecked
            var clearMap = {
                'equipment_pc': { input: 'pc-model', status: 'pc-status' },
                'equipment_controller': { input: 'controller-model', status: 'controller-status' },
                'equipment_projector': { input: 'projector-model', status: 'projector-status' }
            };
            var clearItem = clearMap[name];
            if (clearItem) {
                var inputEl = document.getElementById(clearItem.input);
                var statusEl = document.getElementById(clearItem.status);
                if (inputEl) {
                    inputEl.value = '';
                    inputEl.placeholder = 'Auto-detected when selected';
                }
                if (statusEl) {
                    statusEl.className = 'verification-status';
                    statusEl.innerHTML = '';
                }
            }

            // Stop monitoring controller when unchecked
            if (name === 'equipment_controller') {
                controllerSelected = false;
                controllerDetected = false;
                stopControllerPolling();
                hideControllerWarning();
                // Clear MIDI detection
                midiDevicesDetected = [];
                var midiListEl = document.getElementById('midi-device-list');
                if (midiListEl) {
                    midiListEl.innerHTML = '';
                }
            }
        }

        // Recalculate payment
        calculatePayment();
    });
});

// =========================
// AUTO-SELECT PC ON PAGE LOAD
// =========================

(function () {
    var pcCheckbox = document.querySelector('input[name="equipment_pc"]');
    if (pcCheckbox) {
        pcCheckbox.checked = true;
        var pcItem = pcCheckbox.closest('.equipment-item');
        if (pcItem) {
            pcItem.classList.add('active');
        }
        // Auto-detect PC model on load
        detectPCModel();
        // Trigger initial payment calculation
        calculatePayment();
    }
})();

// =========================
// AUTOMATIC HARDWARE DETECTION
// =========================

// --- PC / Laptop Auto-Detect ---
function detectPCModel() {
    var modelInput = document.getElementById('pc-model');
    var statusEl = document.getElementById('pc-status');

    if (!modelInput || !statusEl) return;

    // Show loading state
    modelInput.value = '';
    modelInput.placeholder = 'Detecting computer...';
    statusEl.className = 'verification-status checking';
    statusEl.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Reading system information...';

    // Use a short delay to show the loading animation, then read real data
    setTimeout(function () {
        var model = getRealPCModel();

        if (model) {
            modelInput.value = model;
            modelInput.placeholder = 'Auto-detected';
            statusEl.className = 'verification-status verified';
            statusEl.innerHTML = '<i class="fas fa-check-circle"></i> Detected: ' + model;
        } else {
            modelInput.placeholder = 'Could not detect model';
            statusEl.className = 'verification-status failed';
            statusEl.innerHTML = '<i class="fas fa-times-circle"></i> Model detection unavailable';
        }
    }, 800);
}

function getRealPCModel() {
    // Method 1: Try Navigator UA Data Hints API (Chrome 100+, opt-in)
    if (navigator.userAgentData && navigator.userAgentData.getHighEntropyValues) {
        try {
            var hints = ['model', 'platform', 'architecture', 'bitness', 'mobile', 'platformVersion'];
            // Synchronous attempt — in real usage this is async, but we use sync fallbacks
        } catch (e) {
            // Not available
        }
    }

    // Method 2: Read from User Agent string — extract real model info
    var ua = navigator.userAgent;

    // Windows: extract from common patterns
    // Look for HP, Dell, Lenovo, ASUS, Acer, MSI, Samsung, Toshiba, Sony, etc.
    var vendors = ['HP ', 'Hewlett-Packard', 'Dell', 'Lenovo', 'ASUS', 'Acer', 'MSI', 'Samsung', 'Toshiba', 'Sony', 'Microsoft Surface', 'Apple MacBook', 'Apple iMac', 'Apple Mac Pro', 'Apple Mac mini'];
    var vendor = '';
    for (var i = 0; i < vendors.length; i++) {
        if (ua.indexOf(vendors[i]) !== -1) {
            vendor = vendors[i].trim();
            break;
        }
    }

    // Method 3: Try to get model from screen and hardware concurrency
    var screenInfo = '';
    if (screen.width && screen.height) {
        screenInfo = screen.width + 'x' + screen.height;
    }

    // Method 4: Try Battery API to confirm laptop vs desktop
    var isLaptop = false;
    if (navigator.getBattery) {
        // Battery API available — likely a laptop
        isLaptop = true;
    }

    // Method 5: Try WebGL renderer for GPU info (real hardware)
    var gpuInfo = getGPUInfo();

    // Build the model string from real detected data
    var model = '';

    if (vendor) {
        model = vendor;
    }

    // Add platform info
    var platform = navigator.platform || '';
    if (platform && model.indexOf(platform) === -1) {
        if (model) model += ' ';
        model += platform;
    }

    // Add device type
    if (isLaptop && model.indexOf('Laptop') === -1 && model.indexOf('MacBook') === -1) {
        if (model) model += ' ';
        model += 'Laptop';
    } else if (!isLaptop && model.indexOf('Desktop') === -1 && model.indexOf('iMac') === -1 && model.indexOf('Mac Pro') === -1) {
        if (model) model += ' ';
        model += 'Desktop';
    }

    // Add GPU info if available
    if (gpuInfo && model.indexOf(gpuInfo) === -1) {
        model += ' (' + gpuInfo + ')';
    }

    // Add screen resolution
    model += ' — ' + screenInfo;

    // Add CPU cores
    var cores = navigator.hardwareConcurrency || 'N/A';
    model += ' | ' + cores + ' cores';

    return model || null;
}

function getGPUInfo() {
    try {
        var canvas = document.createElement('canvas');
        var gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
        if (gl) {
            var debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
            if (debugInfo) {
                var renderer = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
                // Clean up the renderer string to show brand/model
                // e.g. "Intel(R) UHD Graphics 630" or "NVIDIA GeForce GTX 1650"
                return renderer;
            }
        }
    } catch (e) {
        // WebGL not available
    }
    return null;
}

// --- Controller Auto-Detect ---
// This function orchestrates the detection: tries MIDI first, then falls back to USB
function detectController() {
    var modelInput = document.getElementById('controller-model');
    var statusEl = document.getElementById('controller-status');
    var warningEl = document.getElementById('controller-warning');

    if (!modelInput || !statusEl) return;

    modelInput.value = '';
    modelInput.placeholder = 'Scanning for connected controllers...';
    statusEl.className = 'verification-status checking';
    statusEl.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Scanning for MIDI and USB controllers...';

    // Hide warning while scanning
    if (warningEl) {
        warningEl.style.display = 'none';
    }

    // Try Web MIDI API first (most reliable for DJ controllers)
    if (navigator.requestMIDIAccess) {
        detectMIDIDevices(function (midiFound) {
            // If MIDI detection didn't find anything, fall back to USB
            if (!midiFound) {
                detectUSBController();
            }
        });
    } else {
        // No MIDI API — fall back to USB
        console.log('Web MIDI API not available, falling back to USB detection');
        detectUSBController();
    }
}

// USB-only detection (called as fallback after MIDI)
function detectUSBController() {
    var modelInput = document.getElementById('controller-model');
    var statusEl = document.getElementById('controller-status');
    var warningEl = document.getElementById('controller-warning');

    if (!modelInput || !statusEl) return;

    // Only update status if MIDI didn't already find something
    if (!controllerDetected) {
        statusEl.className = 'verification-status checking';
        statusEl.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Scanning USB devices...';
    } else {
        // MIDI already found a device, skip USB
        return;
    }

    // Try async USB detection
    if (navigator.usb) {
        navigator.usb.getDevices().then(function (devices) {
            if (controllerDetected) return; // MIDI already found something

            var found = findControllerInDevices(devices);
            if (found) {
                controllerDetected = true;
                modelInput.value = found;
                modelInput.placeholder = 'Auto-detected';
                statusEl.className = 'verification-status verified';
                statusEl.innerHTML = '<i class="fas fa-check-circle"></i> Connected: ' + found;
                hideControllerWarning();
                stopControllerPolling();
                return;
            }
            // Fallback: check plugins
            var pluginFound = checkPluginsForController();
            if (pluginFound) {
                controllerDetected = true;
                modelInput.value = pluginFound;
                modelInput.placeholder = 'Auto-detected';
                statusEl.className = 'verification-status verified';
                statusEl.innerHTML = '<i class="fas fa-check-circle"></i> Connected: ' + pluginFound;
                hideControllerWarning();
                stopControllerPolling();
                return;
            }
            // No controller found — show warning
            controllerDetected = false;
            modelInput.placeholder = 'No controller detected';
            statusEl.className = 'verification-status failed';
            statusEl.innerHTML = '<i class="fas fa-times-circle"></i> No DJ controller found — plug in your controller';
            showControllerWarning();
        }).catch(function () {
            // USB API error — try plugins
            if (controllerDetected) return; // MIDI already found something

            var pluginFound = checkPluginsForController();
            if (pluginFound) {
                controllerDetected = true;
                modelInput.value = pluginFound;
                modelInput.placeholder = 'Auto-detected';
                statusEl.className = 'verification-status verified';
                statusEl.innerHTML = '<i class="fas fa-check-circle"></i> Connected: ' + pluginFound;
                hideControllerWarning();
                stopControllerPolling();
            } else {
                controllerDetected = false;
                modelInput.placeholder = 'No controller detected';
                statusEl.className = 'verification-status failed';
                statusEl.innerHTML = '<i class="fas fa-times-circle"></i> No DJ controller found — plug in your controller';
                showControllerWarning();
            }
        });
    } else {
        // No USB API — check plugins only
        setTimeout(function () {
            if (controllerDetected) return; // MIDI already found something

            var pluginFound = checkPluginsForController();
            if (pluginFound) {
                controllerDetected = true;
                modelInput.value = pluginFound;
                modelInput.placeholder = 'Auto-detected';
                statusEl.className = 'verification-status verified';
                statusEl.innerHTML = '<i class="fas fa-check-circle"></i> Connected: ' + pluginFound;
                hideControllerWarning();
                stopControllerPolling();
            } else {
                controllerDetected = false;
                modelInput.placeholder = 'No controller detected';
                statusEl.className = 'verification-status failed';
                statusEl.innerHTML = '<i class="fas fa-times-circle"></i> No DJ controller found — plug in your controller';
                showControllerWarning();
            }
        }, 1000);
    }
}

function showControllerWarning() {
    var warningEl = document.getElementById('controller-warning');
    if (warningEl && controllerSelected && !controllerDetected) {
        warningEl.style.display = 'flex';
    }
}

function hideControllerWarning() {
    var warningEl = document.getElementById('controller-warning');
    if (warningEl) {
        warningEl.style.display = 'none';
    }
}

// Known DJ controller vendor IDs (USB VID)
var djVendorIds = {
    '041e': 'Samson',
    '08bb': 'C-Media',
    '0d8c': 'Razer',
    '10f5': 'Pioneer',
    '154e': 'Numark',
    '1604': 'Native Instruments',
    '16d0': 'Roland',
    '17cc': 'Behringer',
    '1869': 'Denon DJ',
    '1b3f': 'Numark',
    '1c4f': 'Pioneer DJ',
    '265a': 'Pioneer DJ',
    '2850': 'Numark',
    '2936': 'Pioneer DJ',
    '2b04': 'Pioneer DJ',
    '2d12': 'Pioneer DJ',
    '30c3': 'Pioneer DJ',
    '311d': 'Pioneer DJ',
    '3282': 'Pioneer DJ',
    '34e6': 'Pioneer DJ',
    '356e': 'Pioneer DJ',
    '3708': 'Pioneer DJ',
    '3712': 'Pioneer DJ',
    '3730': 'Pioneer DJ',
    '3769': 'Pioneer DJ',
    '3822': 'Pioneer DJ',
    '38e4': 'Pioneer DJ',
    '3938': 'Pioneer DJ',
    '39b7': 'Pioneer DJ',
    '3a19': 'Pioneer DJ',
    '3a95': 'Pioneer DJ',
    '3b29': 'Pioneer DJ',
    '3c1f': 'Pioneer DJ',
    '3d11': 'Pioneer DJ',
    '3e1d': 'Pioneer DJ',
    '3f17': 'Pioneer DJ'
};

function findControllerInDevices(devices) {
    for (var i = 0; i < devices.length; i++) {
        var device = devices[i];
        var vid = device.vendorId.toString(16).toLowerCase().padStart(4, '0');
        if (djVendorIds[vid]) {
            var name = djVendorIds[vid];
            if (device.productName) {
                name += ' ' + device.productName;
            } else if (device.productId) {
                name += ' (0x' + device.productId.toString(16) + ')';
            }
            return name;
        }
        // Also check manufacturer/product names for DJ keywords
        var mName = (device.manufacturerName || '').toLowerCase();
        var pName = (device.productName || '').toLowerCase();
        if (mName.indexOf('pioneer') !== -1 || mName.indexOf('numark') !== -1 ||
            mName.indexOf('roland') !== -1 || mName.indexOf('behinger') !== -1 ||
            mName.indexOf('native instruments') !== -1 || pName.indexOf('serato') !== -1 ||
            pName.indexOf('rekordbox') !== -1 || pName.indexOf('traktor') !== -1 ||
            pName.indexOf('controller') !== -1 || pName.indexOf('turntable') !== -1 ||
            pName.indexOf('mixer') !== -1) {
            var fullName = '';
            if (device.manufacturerName) fullName += device.manufacturerName + ' ';
            if (device.productName) fullName += device.productName;
            return fullName || djVendorIds[vid] || 'DJ Controller';
        }
    }
    return null;
}

function checkPluginsForController() {
    var plugins = navigator.plugins;
    if (plugins) {
        for (var j = 0; j < plugins.length; j++) {
            var pluginName = plugins[j].name.toLowerCase();
            if (pluginName.indexOf('serato') !== -1 || pluginName.indexOf('rekordbox') !== -1 ||
                pluginName.indexOf('traktor') !== -1 || pluginName.indexOf('pioneer') !== -1 ||
                pluginName.indexOf('numark') !== -1 || pluginName.indexOf('native instruments') !== -1 ||
                pluginName.indexOf('behinger') !== -1 || pluginName.indexOf('roland') !== -1) {
                return plugins[j].name;
            }
        }
    }
    return null;
}

// =========================
// WEB MIDI API DETECTION
// =========================

// Request MIDI access and enumerate all connected MIDI devices
// callback: optional function called with (midiFound: boolean) when detection completes
function detectMIDIDevices(callback) {
    var modelInput = document.getElementById('controller-model');
    var statusEl = document.getElementById('controller-status');
    var midiListEl = document.getElementById('midi-device-list');

    if (!statusEl) {
        if (typeof callback === 'function') callback(false);
        return;
    }

    // Check if Web MIDI API is supported
    if (!navigator.requestMIDIAccess) {
        console.log('Web MIDI API not supported in this browser');
        if (typeof callback === 'function') callback(false);
        return;
    }

    // Show loading state for MIDI
    statusEl.className = 'verification-status checking';
    statusEl.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Scanning for MIDI devices...';

    console.log('Requesting MIDI access...');

    // Request MIDI access
    navigator.requestMIDIAccess({ sysex: true }).then(
        function (access) {
            midiAccess = access;
            midiDevicesDetected = [];
            midiState = access.inputs;

            console.log('MIDI access granted. Inputs:', midiState.size, 'Outputs:', access.outputs.size);

            // Collect all MIDI devices from inputs
            var allDevices = [];
            var inputList = midiState.values(); // FIXED: was midiState.inputs.values()

            inputList.forEach(function (device) {
                console.log('Found MIDI input:', device.name, 'by', device.manufacturer, 'state:', device.state);
                var deviceInfo = {
                    name: device.name || 'Unknown MIDI Device',
                    manufacturer: device.manufacturer || 'Unknown Manufacturer',
                    type: 'input',
                    state: device.state,
                    version: device.version || 'N/A',
                    id: device.id,
                    connected: device.state === 'connected'
                };
                allDevices.push(deviceInfo);
                if (device.state === 'connected') {
                    midiDevicesDetected.push(deviceInfo);
                }
            });

            // Also check outputs
            var outputList = access.outputs.values();
            outputList.forEach(function (device) {
                console.log('Found MIDI output:', device.name, 'by', device.manufacturer, 'state:', device.state);
                var deviceInfo = {
                    name: device.name || 'Unknown MIDI Device',
                    manufacturer: device.manufacturer || 'Unknown Manufacturer',
                    type: 'output',
                    state: device.state,
                    version: device.version || 'N/A',
                    id: device.id,
                    connected: device.state === 'connected'
                };
                // Avoid duplicates — check if already in list
                var exists = false;
                for (var i = 0; i < allDevices.length; i++) {
                    if (allDevices[i].id === device.id) {
                        exists = true;
                        allDevices[i].type = 'input/output';
                        break;
                    }
                }
                if (!exists) {
                    allDevices.push(deviceInfo);
                }
                if (device.state === 'connected') {
                    var alreadyDetected = false;
                    for (var j = 0; j < midiDevicesDetected.length; j++) {
                        if (midiDevicesDetected[j].id === device.id) {
                            alreadyDetected = true;
                            break;
                        }
                    }
                    if (!alreadyDetected) {
                        midiDevicesDetected.push(deviceInfo);
                    }
                }
            });

            console.log('Total MIDI devices detected:', midiDevicesDetected.length);

            // Update UI with MIDI device list
            if (midiListEl) {
                midiListEl.innerHTML = '';
                if (midiDevicesDetected.length > 0) {
                    midiDevicesDetected.forEach(function (device, index) {
                        var deviceEl = document.createElement('div');
                        deviceEl.className = 'midi-device-item';
                        deviceEl.innerHTML =
                            '<div class="midi-device-icon"><i class="fas fa-music"></i></div>' +
                            '<div class="midi-device-info">' +
                                '<div class="midi-device-name">' + escapeHtml(device.name) + '</div>' +
                                '<div class="midi-device-details">' +
                                    '<span class="midi-manufacturer">' + escapeHtml(device.manufacturer) + '</span>' +
                                    '<span class="midi-type-badge ' + device.type + '">' + device.type + '</span>' +
                                    '<span class="midi-version">v' + escapeHtml(device.version) + '</span>' +
                                '</div>' +
                                '<div class="midi-status-connected"><i class="fas fa-check-circle"></i> Connected</div>' +
                            '</div>';
                        midiListEl.appendChild(deviceEl);
                    });

                    // Update model input with first MIDI device name
                    if (modelInput && midiDevicesDetected.length > 0) {
                        modelInput.value = midiDevicesDetected[0].manufacturer + ' ' + midiDevicesDetected[0].name;
                        modelInput.placeholder = 'MIDI Auto-detected';
                    }

                    // Update status
                    if (statusEl) {
                        controllerDetected = true;
                        statusEl.className = 'verification-status verified';
                        statusEl.innerHTML = '<i class="fas fa-check-circle"></i> ' + midiDevicesDetected.length + ' MIDI device(s) detected';
                        hideControllerWarning();
                        stopControllerPolling();
                    }

                    // Listen for MIDI state changes (connect/disconnect)
                    access.onstatechange = onMIDIStateChange;

                    if (typeof callback === 'function') callback(true);
                } else {
                    // No connected MIDI devices
                    if (midiListEl) {
                        midiListEl.innerHTML = '<div class="midi-no-devices"><i class="fas fa-plug"></i> No MIDI devices connected</div>';
                    }

                    // Don't update status here — let the fallback (USB) update it
                    // Only update status if there's no callback (direct call)
                    if (typeof callback !== 'function') {
                        statusEl.className = 'verification-status failed';
                        statusEl.innerHTML = '<i class="fas fa-times-circle"></i> No MIDI devices found — connect your MIDI controller';
                        showControllerWarning();
                    }

                    // Listen for MIDI state changes even when no devices are connected
                    access.onstatechange = onMIDIStateChange;

                    if (typeof callback === 'function') callback(false);
                }
            } else {
                // No midiListEl — still report results
                if (midiDevicesDetected.length > 0) {
                    if (modelInput) {
                        modelInput.value = midiDevicesDetected[0].manufacturer + ' ' + midiDevicesDetected[0].name;
                        modelInput.placeholder = 'MIDI Auto-detected';
                    }
                    if (statusEl) {
                        controllerDetected = true;
                        statusEl.className = 'verification-status verified';
                        statusEl.innerHTML = '<i class="fas fa-check-circle"></i> ' + midiDevicesDetected.length + ' MIDI device(s) detected';
                        hideControllerWarning();
                        stopControllerPolling();
                    }
                    access.onstatechange = onMIDIStateChange;
                    if (typeof callback === 'function') callback(true);
                } else {
                    if (typeof callback === 'function') callback(false);
                }
            }
        },
        function (error) {
            // MIDI access denied or error
            console.log('MIDI access denied or error:', error);
            if (typeof callback === 'function') callback(false);
        }
    );
}

// Handle MIDI device state changes (connect/disconnect)
function onMIDIStateChange(event) {
    var midiListEl = document.getElementById('midi-device-list');
    var statusEl = document.getElementById('controller-status');
    var modelInput = document.getElementById('controller-model');

    if (!midiAccess) return;

    // Re-scan all MIDI devices
    midiDevicesDetected = [];
    var inputs = midiAccess.inputs.values();

    inputs.forEach(function (device) {
        if (device.state === 'connected') {
            var deviceInfo = {
                name: device.name || 'Unknown MIDI Device',
                manufacturer: device.manufacturer || 'Unknown Manufacturer',
                type: 'input',
                state: device.state,
                version: device.version || 'N/A',
                id: device.id,
                connected: true
            };
            midiDevicesDetected.push(deviceInfo);
        }
    });

    // Also check outputs
    var outputs = midiAccess.outputs.values();
    outputs.forEach(function (device) {
        if (device.state === 'connected') {
            var alreadyExists = false;
            for (var i = 0; i < midiDevicesDetected.length; i++) {
                if (midiDevicesDetected[i].id === device.id) {
                    alreadyExists = true;
                    midiDevicesDetected[i].type = 'input/output';
                    break;
                }
            }
            if (!alreadyExists) {
                midiDevicesDetected.push({
                    name: device.name || 'Unknown MIDI Device',
                    manufacturer: device.manufacturer || 'Unknown Manufacturer',
                    type: 'output',
                    state: device.state,
                    version: device.version || 'N/A',
                    id: device.id,
                    connected: true
                });
            }
        }
    });

    // Update UI
    if (midiListEl) {
        midiListEl.innerHTML = '';
        if (midiDevicesDetected.length > 0) {
            midiDevicesDetected.forEach(function (device) {
                var deviceEl = document.createElement('div');
                deviceEl.className = 'midi-device-item';
                deviceEl.innerHTML =
                    '<div class="midi-device-icon"><i class="fas fa-music"></i></div>' +
                    '<div class="midi-device-info">' +
                        '<div class="midi-device-name">' + escapeHtml(device.name) + '</div>' +
                        '<div class="midi-device-details">' +
                            '<span class="midi-manufacturer">' + escapeHtml(device.manufacturer) + '</span>' +
                            '<span class="midi-type-badge ' + device.type + '">' + device.type + '</span>' +
                            '<span class="midi-version">v' + escapeHtml(device.version) + '</span>' +
                        '</div>' +
                        '<div class="midi-status-connected"><i class="fas fa-check-circle"></i> Connected</div>' +
                    '</div>';
                midiListEl.appendChild(deviceEl);
            });

            if (modelInput) {
                modelInput.value = midiDevicesDetected[0].manufacturer + ' ' + midiDevicesDetected[0].name;
                modelInput.placeholder = 'MIDI Auto-detected';
            }

            if (statusEl) {
                controllerDetected = true;
                statusEl.className = 'verification-status verified';
                statusEl.innerHTML = '<i class="fas fa-check-circle"></i> ' + midiDevicesDetected.length + ' MIDI device(s) detected';
                hideControllerWarning();
                stopControllerPolling();
            }
        } else {
            midiListEl.innerHTML = '<div class="midi-no-devices"><i class="fas fa-plug"></i> No MIDI devices connected</div>';
            if (statusEl) {
                statusEl.className = 'verification-status failed';
                statusEl.innerHTML = '<i class="fas fa-times-circle"></i> No MIDI devices found';
                showControllerWarning();
            }
        }
    }

    // Recalculate payment
    calculatePayment();
}

// Helper to escape HTML to prevent XSS
function escapeHtml(text) {
    var div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// =========================
// USB CONNECTION MONITORING
// =========================

// Listen for USB device connect events (real-time detection when controller is plugged in)
if (navigator.usb) {
    navigator.usb.addEventListener('connect', function (event) {
        // Only check if controller checkbox is selected and not yet detected
        if (controllerSelected && !controllerDetected) {
            var device = event.device;
            var vid = device.vendorId.toString(16).toLowerCase().padStart(4, '0');

            // Check if the connected device is a DJ controller
            if (djVendorIds[vid]) {
                var name = djVendorIds[vid];
                if (device.productName) {
                    name += ' ' + device.productName;
                } else if (device.productId) {
                    name += ' (0x' + device.productId.toString(16) + ')';
                }
                onControllerConnected(name);
                return;
            }

            // Also check manufacturer/product names for DJ keywords
            var mName = (device.manufacturerName || '').toLowerCase();
            var pName = (device.productName || '').toLowerCase();
            if (mName.indexOf('pioneer') !== -1 || mName.indexOf('numark') !== -1 ||
                mName.indexOf('roland') !== -1 || mName.indexOf('behinger') !== -1 ||
                mName.indexOf('native instruments') !== -1 || pName.indexOf('serato') !== -1 ||
                pName.indexOf('rekordbox') !== -1 || pName.indexOf('traktor') !== -1 ||
                pName.indexOf('controller') !== -1 || pName.indexOf('turntable') !== -1 ||
                pName.indexOf('mixer') !== -1) {
                var fullName = '';
                if (device.manufacturerName) fullName += device.manufacturerName + ' ';
                if (device.productName) fullName += device.productName;
                onControllerConnected(fullName || 'DJ Controller');
                return;
            }
        }
    });

    // Listen for USB device disconnect events
    navigator.usb.addEventListener('disconnect', function () {
        if (controllerDetected) {
            controllerDetected = false;
            var modelInput = document.getElementById('controller-model');
            var statusEl = document.getElementById('controller-status');
            if (modelInput) {
                modelInput.value = '';
                modelInput.placeholder = 'Controller disconnected';
            }
            if (statusEl) {
                statusEl.className = 'verification-status failed';
                statusEl.innerHTML = '<i class="fas fa-times-circle"></i> Controller disconnected — plug in your controller';
            }
            showControllerWarning();
            startControllerPolling();
        }
    });
}

// Handle successful controller connection detection
function onControllerConnected(name) {
    controllerDetected = true;
    var modelInput = document.getElementById('controller-model');
    var statusEl = document.getElementById('controller-status');

    if (modelInput) {
        modelInput.value = name;
        modelInput.placeholder = 'Auto-detected';
    }
    if (statusEl) {
        statusEl.className = 'verification-status verified';
        statusEl.innerHTML = '<i class="fas fa-check-circle"></i> Connected: ' + name;
    }
    hideControllerWarning();
    stopControllerPolling();

    // Recalculate payment since equipment changed
    calculatePayment();
}

// Periodic polling fallback for browsers without USB connect event support
// Also re-checks MIDI devices in case a controller was plugged in after page load
function startControllerPolling() {
    // Clear any existing interval
    stopControllerPolling();

    // Poll every 3 seconds to check for newly connected controller
    controllerPollInterval = setInterval(function () {
        if (!controllerSelected || controllerDetected) {
            stopControllerPolling();
            return;
        }

        // First try MIDI re-scan if we already have MIDI access
        if (midiAccess) {
            var midiInputs = midiAccess.inputs.values();
            var foundMidi = false;
            midiInputs.forEach(function (device) {
                if (device.state === 'connected' && !foundMidi) {
                    foundMidi = true;
                    var name = (device.manufacturer || '') + ' ' + (device.name || 'MIDI Controller');
                    onControllerConnected(name);
                }
            });
            if (foundMidi) return;
        }

        // Try USB detection
        if (navigator.usb) {
            navigator.usb.getDevices().then(function (devices) {
                if (controllerDetected) return; // MIDI found it first
                var found = findControllerInDevices(devices);
                if (found) {
                    onControllerConnected(found);
                } else {
                    // Fallback: check plugins
                    var pluginFound = checkPluginsForController();
                    if (pluginFound) {
                        onControllerConnected(pluginFound);
                    }
                }
            }).catch(function () {
                // USB API error — try plugins
                if (controllerDetected) return;
                var pluginFound = checkPluginsForController();
                if (pluginFound) {
                    onControllerConnected(pluginFound);
                }
            });
        } else {
            // No USB API — check plugins only
            if (controllerDetected) return;
            var pluginFound = checkPluginsForController();
            if (pluginFound) {
                onControllerConnected(pluginFound);
            }
        }
    }, 3000);
}

function stopControllerPolling() {
    if (controllerPollInterval) {
        clearInterval(controllerPollInterval);
        controllerPollInterval = null;
    }
}

// --- Projector Auto-Detect ---
function detectProjector() {
    var modelInput = document.getElementById('projector-model');
    var statusEl = document.getElementById('projector-status');

    if (!modelInput || !statusEl) return;

    modelInput.value = '';
    modelInput.placeholder = 'Scanning for connected displays...';
    statusEl.className = 'verification-status checking';
    statusEl.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Detecting connected displays...';

    // Try async USB detection
    if (navigator.usb) {
        navigator.usb.getDevices().then(function (devices) {
            var found = findProjectorInDevices(devices);
            if (found) {
                modelInput.value = found;
                modelInput.placeholder = 'Auto-detected';
                statusEl.className = 'verification-status verified';
                statusEl.innerHTML = '<i class="fas fa-check-circle"></i> Connected: ' + found;
                return;
            }
            // Fallback: check for secondary displays
            var secondary = checkSecondaryDisplays();
            if (secondary) {
                modelInput.value = secondary;
                modelInput.placeholder = 'Auto-detected';
                statusEl.className = 'verification-status verified';
                statusEl.innerHTML = '<i class="fas fa-check-circle"></i> Connected: ' + secondary;
                return;
            }
            modelInput.placeholder = 'No projector detected';
            statusEl.className = 'verification-status failed';
            statusEl.innerHTML = '<i class="fas fa-times-circle"></i> No projector found — connect your projector';
        }).catch(function () {
            var secondary = checkSecondaryDisplays();
            if (secondary) {
                modelInput.value = secondary;
                modelInput.placeholder = 'Auto-detected';
                statusEl.className = 'verification-status verified';
                statusEl.innerHTML = '<i class="fas fa-check-circle"></i> Connected: ' + secondary;
            } else {
                modelInput.placeholder = 'No projector detected';
                statusEl.className = 'verification-status failed';
                statusEl.innerHTML = '<i class="fas fa-times-circle"></i> No projector found — connect your projector';
            }
        });
    } else {
        // No USB API — check secondary displays only
        setTimeout(function () {
            var secondary = checkSecondaryDisplays();
            if (secondary) {
                modelInput.value = secondary;
                modelInput.placeholder = 'Auto-detected';
                statusEl.className = 'verification-status verified';
                statusEl.innerHTML = '<i class="fas fa-check-circle"></i> Connected: ' + secondary;
            } else {
                modelInput.placeholder = 'No projector detected';
                statusEl.className = 'verification-status failed';
                statusEl.innerHTML = '<i class="fas fa-times-circle"></i> No projector found — connect your projector';
            }
        }, 1000);
    }
}

function findProjectorInDevices(devices) {
    var projectorBrands = ['epson', 'benq', 'optoma', 'viewsonic', 'lg', 'samsung', 'sony', 'panasonic', 'canon', 'sharp', 'neovision', 'mimaki', 'infocus'];
    for (var i = 0; i < devices.length; i++) {
        var device = devices[i];
        var mName = (device.manufacturerName || '').toLowerCase();
        var pName = (device.productName || '').toLowerCase();
        var combined = mName + ' ' + pName;
        for (var j = 0; j < projectorBrands.length; j++) {
            if (combined.indexOf(projectorBrands[j]) !== -1) {
                var name = '';
                if (device.manufacturerName) name += device.manufacturerName + ' ';
                if (device.productName) name += device.productName;
                return name || 'Projector';
            }
        }
        if (pName.indexOf('projector') !== -1 || pName.indexOf('beamer') !== -1) {
            var name2 = '';
            if (device.manufacturerName) name2 += device.manufacturerName + ' ';
            if (device.productName) name2 += device.productName;
            return name2 || 'Projector';
        }
    }
    return null;
}

function checkSecondaryDisplays() {
    // Check for multiple screens via screen API
    if (window.screen && window.screen.getDetails) {
        try {
            var details = window.screen.getDetails();
            if (details && details.length > 1) {
                var names = [];
                for (var i = 1; i < details.length; i++) {
                    var s = details[i];
                    var name = '';
                    if (s.deviceIdPart) name += s.deviceIdPart + ' ';
                    if (s.name) name += s.name;
                    if (!name) name = 'Display ' + (i);
                    name += ' (' + s.availWidth + 'x' + s.availHeight + ')';
                    names.push(name);
                }
                return names.join(', ');
            }
        } catch (e) {
            // API not available
        }
    }
    return null;
}

// =========================
// EQUIPMENT IMAGE PREVIEWS
// =========================

var imageUploads = [
    { input: 'mixer-image', preview: 'mixer-image-preview' },
    { input: 'speakers-image', preview: 'speakers-image-preview' },
    { input: 'generator-image', preview: 'generator-image-preview' },
    { input: 'microphones-image', preview: 'microphones-image-preview' },
    { input: 'instruments-image', preview: 'instruments-image-preview' }
];

imageUploads.forEach(function (item) {
    var inputEl = document.getElementById(item.input);
    var previewEl = document.getElementById(item.preview);

    if (inputEl && previewEl) {
        inputEl.addEventListener('change', function (e) {
            previewEl.innerHTML = '';
            var files = e.target.files;

            for (var i = 0; i < files.length; i++) {
                var file = files[i];
                var reader = new FileReader();
                reader.onload = function (event) {
                    var img = document.createElement('img');
                    img.src = event.target.result;
                    previewEl.appendChild(img);
                };
                reader.readAsDataURL(file);
            }

            // Recalculate payment when image is uploaded (may verify equipment)
            calculatePayment();
        });
    }
});

// =========================
// PAYMENT CALCULATION
// =========================

function calculatePayment() {
    var dailyRate = parseFloat(document.getElementById('daily-rate').value) || 0;

    // Check which equipment is selected
    var hasPc = document.querySelector('input[name="equipment_pc"]').checked;
    var hasController = document.querySelector('input[name="equipment_controller"]').checked;
    var hasMixer = document.querySelector('input[name="equipment_mixer"]').checked;
    var hasSpeakers = document.querySelector('input[name="equipment_speakers"]').checked;
    var hasGenerator = document.querySelector('input[name="equipment_generator"]').checked;
    var hasProjector = document.querySelector('input[name="equipment_projector"]').checked;
    var hasMicrophones = document.querySelector('input[name="equipment_microphones"]').checked;
    var hasInstruments = document.querySelector('input[name="equipment_instruments"]').checked;

    // Get speakers quantity
    var speakersQty = parseInt(document.getElementById('speakers-quantity').value) || 0;

    // Check verification status for each equipment
    var pcStatus = getVerificationStatus('pc-status');
    var controllerStatus = getVerificationStatus('controller-status');
    var projectorStatus = getVerificationStatus('projector-status');

    // For image-based equipment, verified if checkbox is checked and image is uploaded
    var mixerStatus = hasMixer && hasImageUploaded('mixer-image') ? 'verified' : (hasMixer ? 'selected' : '');
    var speakersStatus = hasSpeakers && hasImageUploaded('speakers-image') ? 'verified' : (hasSpeakers ? 'selected' : '');
    var generatorStatus = hasGenerator && hasImageUploaded('generator-image') ? 'verified' : (hasGenerator ? 'selected' : '');
    var microphonesStatus = hasMicrophones && hasImageUploaded('microphones-image') ? 'verified' : (hasMicrophones ? 'selected' : '');
    var instrumentsStatus = hasInstruments && hasImageUploaded('instruments-image') ? 'verified' : (hasInstruments ? 'selected' : '');

    // Build equipment breakdown data — only include items that are selected AND verified
    var equipmentItems = [];

    if (hasPc && pcStatus === 'verified') {
        equipmentItems.push({ name: 'PC / Laptop', value: 700, icon: 'fa-laptop', verified: true });
    } else if (hasPc) {
        equipmentItems.push({ name: 'PC / Laptop', value: 700, icon: 'fa-laptop', verified: false });
    }

    if (hasController && controllerStatus === 'verified') {
        equipmentItems.push({ name: 'Controller', value: 800, icon: 'fa-compact-disc', verified: true });
    } else if (hasController) {
        equipmentItems.push({ name: 'Controller', value: 800, icon: 'fa-compact-disc', verified: false });
    }

    if (hasMixer && mixerStatus === 'verified') {
        equipmentItems.push({ name: 'Mixer', value: 3000, icon: 'fa-sliders-h', verified: true });
    } else if (hasMixer) {
        equipmentItems.push({ name: 'Mixer', value: 3000, icon: 'fa-sliders-h', verified: false });
    }

    if (hasSpeakers && speakersStatus === 'verified') {
        equipmentItems.push({ name: 'Speakers (' + speakersQty + ')', value: 3000, icon: 'fa-volume-up', verified: true });
    } else if (hasSpeakers) {
        equipmentItems.push({ name: 'Speakers', value: 3000, icon: 'fa-volume-up', verified: false });
    }

    if (hasGenerator && generatorStatus === 'verified') {
        equipmentItems.push({ name: 'Generator', value: 2000, icon: 'fa-bolt', verified: true });
    } else if (hasGenerator) {
        equipmentItems.push({ name: 'Generator', value: 2000, icon: 'fa-bolt', verified: false });
    }

    if (hasProjector && projectorStatus === 'verified') {
        equipmentItems.push({ name: 'Projector', value: 2000, icon: 'fa-tv', verified: true });
    } else if (hasProjector) {
        equipmentItems.push({ name: 'Projector', value: 2000, icon: 'fa-tv', verified: false });
    }

    if (hasMicrophones && microphonesStatus === 'verified') {
        equipmentItems.push({ name: 'Microphones', value: 1500, icon: 'fa-microphone', verified: true });
    } else if (hasMicrophones) {
        equipmentItems.push({ name: 'Microphones', value: 1500, icon: 'fa-microphone', verified: false });
    }

    if (hasInstruments && instrumentsStatus === 'verified') {
        equipmentItems.push({ name: 'Instruments', value: 2000, icon: 'fa-guitar', verified: true });
    } else if (hasInstruments) {
        equipmentItems.push({ name: 'Instruments', value: 2000, icon: 'fa-guitar', verified: false });
    }

    // Calculate equipment value — only verified items count toward payment
    var equipmentValue = 0;
    equipmentItems.forEach(function (item) {
        if (item.verified) {
            equipmentValue += item.value;
        }
    });

    // Update the dynamic equipment breakdown in the payment section
    updateEquipmentBreakdown(equipmentItems);

    // Update payment display
    document.getElementById('pay-daily').textContent = 'KES ' + dailyRate.toLocaleString();
    document.getElementById('pay-equipment').textContent = 'KES ' + equipmentValue.toLocaleString();

    // Calculate total: Daily Rate + Equipment value = Total per event (new daily rate)
    var totalPerEvent = dailyRate + equipmentValue;
    document.getElementById('pay-total').textContent = 'KES ' + totalPerEvent.toLocaleString();
}


// =========================
// HELPER: Get verification status from status element
// =========================

function getVerificationStatus(elementId) {
    var el = document.getElementById(elementId);
    if (!el) return '';
    if (el.classList.contains('verified')) return 'verified';
    if (el.classList.contains('failed')) return 'failed';
    return '';
}


// =========================
// HELPER: Check if image is uploaded for an input
// =========================

function hasImageUploaded(inputId) {
    var input = document.getElementById(inputId);
    if (!input) return false;
    return input.files && input.files.length > 0;
}


// =========================
// UPDATE EQUIPMENT BREAKDOWN UI
// =========================

function updateEquipmentBreakdown(items) {
    var container = document.getElementById('pay-equipment-breakdown');
    if (!container) return;

    // Clear existing content
    container.innerHTML = '';

    if (items.length === 0) {
        container.innerHTML = '<div class="payment-row equipment-empty"><span class="payment-label"><i class="fas fa-headphones"></i> Equipment</span><span class="payment-value">No equipment selected</span></div>';
        return;
    }

    // Build individual rows for each equipment item
    items.forEach(function (item) {
        var row = document.createElement('div');
        row.className = 'payment-row equipment-item-row' + (item.verified ? ' verified' : ' not-verified');

        var labelHtml = '<span class="payment-label equipment-label">' +
            '<i class="fas ' + item.icon + '"></i> ' + escapeHtml(item.name);

        if (!item.verified) {
            labelHtml += ' <span class="verification-badge pending"><i class="fas fa-clock"></i> Pending</span>';
        } else {
            labelHtml += ' <span class="verification-badge done"><i class="fas fa-check"></i> Verified</span>';
        }
        labelHtml += '</span>';

        var valueHtml;
        if (item.verified) {
            valueHtml = '<span class="payment-value equipment-value">KES ' + item.value.toLocaleString() + '</span>';
        } else {
            valueHtml = '<span class="payment-value equipment-value not-counting">KES ' + item.value.toLocaleString() + ' (pending)</span>';
        }

        row.innerHTML = labelHtml + valueHtml;
        container.appendChild(row);
    });
}

// Listen for daily rate changes
var dailyRateInput = document.getElementById('daily-rate');
if (dailyRateInput) {
    dailyRateInput.addEventListener('input', calculatePayment);
}

// Listen for speakers quantity changes (affects package detection)
var speakersQtyInput = document.getElementById('speakers-quantity');
if (speakersQtyInput) {
    speakersQtyInput.addEventListener('input', calculatePayment);
}


