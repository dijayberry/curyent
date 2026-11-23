/* =========================
   LOGIN REDIRECT TIMER (20 seconds)
========================= */

// isLoggedIn is set by server-side template in booking.html

var loginRedirectTimer = null;
var loginRedirectCountdown = null;
var secondsRemaining = 20;

function startLoginRedirectTimer() {
    // Only start timer if user is not logged in
    if (isLoggedIn) {
        return;
    }

    // Show countdown warning
    var countdownEl = document.getElementById('login-countdown');
    if (countdownEl) {
        countdownEl.style.display = 'block';
    }

    // Update countdown every second
    loginRedirectCountdown = setInterval(function () {
        secondsRemaining--;
        if (countdownEl) {
            countdownEl.querySelector('.countdown-number').textContent = secondsRemaining;
        }

        if (secondsRemaining <= 0) {
            clearInterval(loginRedirectCountdown);
            window.location.href = '/account/logi';
        }
    }, 1000);
}

function resetLoginRedirectTimer() {
    // Reset timer on user activity (only if not logged in)
    if (isLoggedIn) {
        return;
    }

    // Clear existing timers
    if (loginRedirectCountdown) {
        clearInterval(loginRedirectCountdown);
    }

    secondsRemaining = 20;
    var countdownEl = document.getElementById('login-countdown');
    if (countdownEl) {
        countdownEl.querySelector('.countdown-number').textContent = secondsRemaining;
    }

    // Restart countdown
    loginRedirectCountdown = setInterval(function () {
        secondsRemaining--;
        if (countdownEl) {
            countdownEl.querySelector('.countdown-number').textContent = secondsRemaining;
        }

        if (secondsRemaining <= 0) {
            clearInterval(loginRedirectCountdown);
            window.location.href = '/account/logi';
        }
    }, 1000);
}

/* =========================
   TAB SWITCHING
========================= */

document.addEventListener('DOMContentLoaded', function () {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    // Function to switch to a specific tab by name
    function switchToTab(tabName) {
        tabButtons.forEach(function (btn) {
            btn.classList.remove('active');
        });
        tabContents.forEach(function (content) {
            content.classList.remove('active');
        });

        const targetBtn = document.querySelector('.tab-btn[data-tab="' + tabName + '"]');
        if (targetBtn) {
            targetBtn.classList.add('active');
        }
        const targetTab = document.getElementById('tab-' + tabName);
        if (targetTab) {
            targetTab.classList.add('active');
        }
    }

    tabButtons.forEach(function (button) {
        button.addEventListener('click', function () {
            switchToTab(this.getAttribute('data-tab'));
        });
    });

    // Check URL parameter for tab switching (e.g. /bookings?tab=received or /bookings?tab=my)
    const urlParams = new URLSearchParams(window.location.search);
    const tabParam = urlParams.get('tab');
    const bookingId = urlParams.get('id');

    if (tabParam === 'received') {
        switchToTab('received-bookings');
    } else if (tabParam === 'my') {
        switchToTab('my-bookings');
    }

    // Scroll to and highlight the specific booking card if id parameter is present
    if (bookingId) {
        // Wait a moment for the tab to switch and content to be visible
        setTimeout(function () {
            const targetCard = document.getElementById('booking-card-' + bookingId);
            if (targetCard) {
                // Scroll the card into view
                targetCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
                // Add highlight class
                targetCard.classList.add('booking-card-highlight');
                // Remove highlight after animation completes
                setTimeout(function () {
                    targetCard.classList.remove('booking-card-highlight');
                }, 3000);
            }
        }, 300);
    }

    // Start login redirect timer on page load
    startLoginRedirectTimer();

    // Reset timer on user interaction
    var activityEvents = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'];
    activityEvents.forEach(function (event) {
        document.addEventListener(event, resetLoginRedirectTimer);
    });
});

/* =========================
   TOAST NOTIFICATION
========================= */

function showToast(message, type) {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toast-message');
    const toastIcon = toast.querySelector('i');

    toastMessage.textContent = message;

    // Set icon based on type
    toastIcon.className = 'fas';
    if (type === 'success') {
        toastIcon.classList.add('fa-check-circle');
        toastIcon.style.color = '#4caf50';
    } else if (type === 'error') {
        toastIcon.classList.add('fa-exclamation-circle');
        toastIcon.style.color = '#ff5252';
    } else {
        toastIcon.classList.add('fa-info-circle');
        toastIcon.style.color = '#c9a0ff';
    }

    toast.classList.add('show');

    setTimeout(function () {
        toast.classList.remove('show');
    }, 3000);
}

/* =========================
   CELEBRATION TYPES
========================= */

var celebrationTypesLoaded = false;

function loadCelebrationTypes() {
    if (celebrationTypesLoaded) return;

    fetch('/api/celebration-types')
    .then(function (response) {
        return response.json();
    })
    .then(function (data) {
        if (data.success) {
            var select = document.getElementById('celebration-type');
            // Clear existing options except the first placeholder
            select.innerHTML = '<option value="">Select a celebration type</option>';
            data.types.forEach(function (type) {
                var option = document.createElement('option');
                option.value = type.name;
                option.textContent = type.name;
                select.appendChild(option);
            });
            // Add "Other (Add New)" option at the end
            var otherOption = document.createElement('option');
            otherOption.value = '__other__';
            otherOption.textContent = '+ Add New Type...';
            select.appendChild(otherOption);
            celebrationTypesLoaded = true;
        }
    })
    .catch(function (error) {
        console.error('Failed to load celebration types:', error);
    });
}

// Show/hide the "add new type" input row
(function () {
    var select = document.getElementById('celebration-type');
    if (select) {
        select.addEventListener('change', function () {
            var addRow = document.getElementById('add-type-row');
            if (this.value === '__other__') {
                addRow.style.display = 'flex';
                document.getElementById('new-celebration-type').focus();
            } else {
                addRow.style.display = 'none';
            }
        });
    }
})();

function addCelebrationType() {
    var input = document.getElementById('new-celebration-type');
    var name = input.value.trim();

    if (!name) {
        showToast('Please enter a celebration type name', 'error');
        return;
    }

    fetch('/api/celebration-types', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name: name })
    })
    .then(function (response) {
        return response.json().then(function (data) {
            if (!response.ok) {
                throw new Error(data.message || 'Failed to add type');
            }
            return data;
        });
    })
    .then(function (data) {
        if (data.success) {
            // Reload types and select the newly added one
            loadCelebrationTypes();
            var select = document.getElementById('celebration-type');
            select.value = data.name;
            document.getElementById('add-type-row').style.display = 'none';
            input.value = '';
            showToast('"' + data.name + '" added successfully!', 'success');
        }
    })
    .catch(function (error) {
        showToast(error.message || 'Failed to add celebration type', 'error');
    });
}

/* =========================
   BOOKING MODAL
========================= */

function openBookingModal(bookedId, bookedRole, dailyRate, username) {
    document.getElementById('modal-profile-name').textContent = username;
    document.getElementById('modal-booked-id').value = bookedId;
    document.getElementById('modal-booked-role').value = bookedRole;
    document.getElementById('modal-daily-rate').value = dailyRate;

    var originalTotal = dailyRate * 1.8;
    document.getElementById('modal-total-display').textContent = 'KES ' + Math.round(originalTotal);

    // Hide loyalty discount rows by default
    document.getElementById('modal-fifth-loyalty').style.display = 'none';
    document.getElementById('modal-final-row').style.display = 'none';

    // Check if this booking qualifies for the 5th-booking loyalty discount
    fetch('/api/book/loyalty-check')
        .then(function (response) { return response.json(); })
        .then(function (data) {
            if (data.is_fifth_booking) {
                var discountAmount = originalTotal * 0.05;
                var finalTotal = originalTotal - discountAmount;
                document.getElementById('modal-fifth-discount-amount').textContent = '-KES ' + Math.round(discountAmount);
                document.getElementById('modal-final-display').textContent = 'KES ' + Math.round(finalTotal);
                document.getElementById('modal-fifth-loyalty').style.display = 'flex';
                document.getElementById('modal-final-row').style.display = 'flex';
            }
        })
        .catch(function () { /* Silently ignore — discount rows stay hidden */ });

    // Load celebration types on first open
    loadCelebrationTypes();

    // Set minimum date to today
    var today = new Date().toISOString().split('T')[0];
    document.getElementById('event-start-date').setAttribute('min', today);
    document.getElementById('event-end-date').setAttribute('min', today);

    // Hide add-type row
    document.getElementById('add-type-row').style.display = 'none';

    document.getElementById('booking-modal').style.display = 'flex';
}

function closeBookingModal() {
    document.getElementById('booking-modal').style.display = 'none';
    document.getElementById('booking-form').reset();
    document.getElementById('add-type-row').style.display = 'none';
}

function submitBooking(event) {
    event.preventDefault();

    var bookedId = parseInt(document.getElementById('modal-booked-id').value);
    var bookedRole = document.getElementById('modal-booked-role').value;
    var dailyRate = parseFloat(document.getElementById('modal-daily-rate').value);
    var eventStartDate = document.getElementById('event-start-date').value;
    var eventEndDate = document.getElementById('event-end-date').value;

    // Celebration details
    var celebrationTypeEl = document.getElementById('celebration-type');
    var celebrationType = celebrationTypeEl.value;
    var celebrationTitle = document.getElementById('celebration-title').value.trim();
    var venueLocation = document.getElementById('venue-location').value.trim();
    var startTime = document.getElementById('start-time').value;
    var endTime = document.getElementById('end-time').value;
    var attendeesCount = document.getElementById('attendees-count').value;

    // Validate celebration type
    if (!celebrationType || celebrationType === '__other__') {
        showToast('Please select a celebration type', 'error');
        return;
    }

    // Validate celebration title
    if (!celebrationTitle) {
        showToast('Please enter a celebration title', 'error');
        return;
    }

    // Validate venue location
    if (!venueLocation) {
        showToast('Please enter a venue location', 'error');
        return;
    }

    // Validate times
    if (!startTime || !endTime) {
        showToast('Please select start and end times', 'error');
        return;
    }

    if (endTime <= startTime) {
        showToast('End time must be after start time', 'error');
        return;
    }

    // Validate attendees
    if (!attendeesCount || parseInt(attendeesCount) <= 0) {
        showToast('Please enter the number of attendees', 'error');
        return;
    }

    if (!eventStartDate) {
        showToast('Please select an event start date', 'error');
        return;
    }

    // Validate end date is after start date
    if (eventEndDate && eventEndDate < eventStartDate) {
        showToast('Event end date must be after start date', 'error');
        return;
    }

    fetch('/api/book', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            booked_id: bookedId,
            booked_role: bookedRole,
            daily_rate: dailyRate,
            event_start_date: eventStartDate,
            event_end_date: eventEndDate || null,
            celebration_type: celebrationType,
            celebration_title: celebrationTitle,
            venue_location: venueLocation,
            start_time: startTime,
            end_time: endTime,
            attendees_count: parseInt(attendeesCount)
        })
    })
    .then(function (response) {
        return response.json().then(function (data) {
            if (!response.ok) {
                throw new Error(data.message || 'Booking failed');
            }
            return data;
        });
    })
    .then(function (data) {
        if (data.success) {
            closeBookingModal();
            if (data.is_fifth_booking) {
                showToast('Booking sent! 5% loyalty discount applied — save KES ' + Math.round(data.discount_amount) + '!', 'success');
            } else {
                showToast('Booking request sent successfully!', 'success');
            }
            setTimeout(function () {
                location.reload();
            }, 1500);
        } else {
            showToast(data.message || 'Booking failed', 'error');
        }
    })
    .catch(function (error) {
        showToast(error.message || 'Something went wrong', 'error');
    });
}

/* =========================
   REJECTION MODAL
========================= */

function openRejectModal(bookingId) {
    document.getElementById('reject-booking-id').value = bookingId;
    document.getElementById('rejection-reason').value = '';
    document.getElementById('reject-modal').style.display = 'flex';
}

function closeRejectModal() {
    document.getElementById('reject-modal').style.display = 'none';
    document.getElementById('reject-form').reset();
}

function submitReject(event) {
    event.preventDefault();

    var bookingId = parseInt(document.getElementById('reject-booking-id').value);
    var reason = document.getElementById('rejection-reason').value.trim();

    if (!reason) {
        showToast('Please provide a reason for rejection', 'error');
        return;
    }

    fetch('/api/booking/' + bookingId + '/reject-service', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            reason: reason
        })
    })
    .then(function (response) {
        return response.json().then(function (data) {
            if (!response.ok) {
                throw new Error(data.message || 'Failed to reject service');
            }
            return data;
        });
    })
    .then(function (data) {
        if (data.success) {
            closeRejectModal();
            showToast('Service rejected. Reason has been recorded.', 'info');
            setTimeout(function () {
                location.reload();
            }, 1500);
        } else {
            showToast(data.message || 'Failed to reject service', 'error');
        }
    })
    .catch(function (error) {
        showToast(error.message || 'Something went wrong', 'error');
    });
}

/* =========================
   ACCEPT BOOKING
========================= */

function acceptBooking(bookingId) {
    if (!confirm('Are you sure you want to accept this booking request?')) {
        return;
    }

    fetch('/api/booking/accept/' + bookingId, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(function (response) {
        return response.json().then(function (data) {
            if (!response.ok) {
                throw new Error(data.message || 'Failed to accept booking');
            }
            return data;
        });
    })
    .then(function (data) {
        if (data.success) {
            showToast('Booking accepted!', 'success');
            // Reload page to update status
            setTimeout(function () {
                location.reload();
            }, 1500);
        } else {
            showToast(data.message || 'Failed to accept booking', 'error');
        }
    })
    .catch(function (error) {
        showToast(error.message || 'Something went wrong', 'error');
    });
}

/* =========================
   DECLINE BOOKING
========================= */

function declineBooking(bookingId) {
    if (!confirm('Are you sure you want to decline this booking request?')) {
        return;
    }

    fetch('/api/booking/decline/' + bookingId, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(function (response) {
        return response.json().then(function (data) {
            if (!response.ok) {
                throw new Error(data.message || 'Failed to decline booking');
            }
            return data;
        });
    })
    .then(function (data) {
        if (data.success) {
            showToast('Booking declined', 'info');
            setTimeout(function () {
                location.reload();
            }, 1500);
        } else {
            showToast(data.message || 'Failed to decline booking', 'error');
        }
    })
    .catch(function (error) {
        showToast(error.message || 'Something went wrong', 'error');
    });
}

/* =========================
   CANCEL BOOKING
========================= */

function cancelBooking(bookingId) {
    if (!confirm('Are you sure you want to cancel this booking? This action cannot be undone.')) {
        return;
    }

    fetch('/api/booking/cancel/' + bookingId, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(function (response) {
        return response.json().then(function (data) {
            if (!response.ok) {
                throw new Error(data.message || 'Failed to cancel booking');
            }
            return data;
        });
    })
    .then(function (data) {
        if (data.success) {
            showToast('Booking cancelled successfully', 'success');
            setTimeout(function () {
                location.reload();
            }, 1500);
        } else {
            showToast(data.message || 'Failed to cancel booking', 'error');
        }
    })
    .catch(function (error) {
        showToast(error.message || 'Something went wrong', 'error');
    });
}

/* =========================
   SERVICE APPROVAL WORKFLOW
========================= */

function requestApproval(bookingId) {
    if (!confirm('Request service approval from the booked person? They will be notified via WhatsApp.')) {
        return;
    }

    fetch('/api/booking/' + bookingId + '/request-approval', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(function (response) {
        return response.json().then(function (data) {
            if (!response.ok) {
                throw new Error(data.message || 'Failed to request approval');
            }
            return data;
        });
    })
    .then(function (data) {
        if (data.success) {
            showToast('Approval request sent! The booked person will be notified.', 'success');
            setTimeout(function () {
                location.reload();
            }, 1500);
        } else {
            showToast(data.message || 'Failed to request approval', 'error');
        }
    })
    .catch(function (error) {
        showToast(error.message || 'Something went wrong', 'error');
    });
}

function approveService(bookingId) {
    if (!confirm('Confirm that you delivered the service? After approval, payout will be processed in 30-60 minutes.')) {
        return;
    }

    fetch('/api/booking/' + bookingId + '/approve-service', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(function (response) {
        return response.json().then(function (data) {
            if (!response.ok) {
                throw new Error(data.message || 'Failed to approve service');
            }
            return data;
        });
    })
    .then(function (data) {
        if (data.success) {
            showToast('Service approved! Payout will be processed in 30-60 minutes.', 'success');
            setTimeout(function () {
                location.reload();
            }, 1500);
        } else {
            showToast(data.message || 'Failed to approve service', 'error');
        }
    })
    .catch(function (error) {
        showToast(error.message || 'Something went wrong', 'error');
    });
}

function processPayout(bookingId) {
    if (!confirm('Process payout to the booked person now?')) {
        return;
    }

    fetch('/api/booking/' + bookingId + '/process-payout', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(function (response) {
        return response.json().then(function (data) {
            if (!response.ok) {
                throw new Error(data.message || 'Failed to process payout');
            }
            return data;
        });
    })
    .then(function (data) {
        if (data.success) {
            showToast('Payout of KES ' + Math.round(data.payout_amount) + ' processed successfully!', 'success');
            setTimeout(function () {
                location.reload();
            }, 1500);
        } else {
            showToast(data.message || 'Failed to process payout', 'error');
        }
    })
    .catch(function (error) {
        showToast(error.message || 'Something went wrong', 'error');
    });
}

/* =========================
   MULTI-BOOKING LOGIC
========================= */

var multiSelectedProviders = [];

function updateMultiSelection() {
    var checkboxes = document.querySelectorAll('.provider-checkbox:checked');
    multiSelectedProviders = [];
    var roles = [];

    checkboxes.forEach(function (cb) {
        multiSelectedProviders.push({
            booked_id: parseInt(cb.dataset.id),
            booked_role: cb.dataset.role,
            daily_rate: parseFloat(cb.dataset.rate),
            username: cb.dataset.username
        });
        roles.push(cb.dataset.role);
    });

    var bar = document.getElementById('multi-booking-bar');
    var countEl = document.getElementById('multi-selected-count');
    var totalEl = document.getElementById('multi-bar-total');
    var saveEl = document.getElementById('multi-bar-save');
    var discountBadge = document.getElementById('multi-discount-badge');

    if (multiSelectedProviders.length >= 2) {
        // Check for duplicate roles
        var uniqueRoles = roles.filter(function (role, index) {
            return roles.indexOf(role) === index;
        });

        if (uniqueRoles.length < roles.length) {
            // Duplicate role found — uncheck the duplicate
            var seen = {};
            checkboxes.forEach(function (cb) {
                if (seen[cb.dataset.role]) {
                    cb.checked = false;
                }
                seen[cb.dataset.role] = true;
            });
            showToast('Cannot select the same role twice', 'error');
            updateMultiSelection();
            return;
        }

        bar.style.display = 'block';
        countEl.textContent = multiSelectedProviders.length;

        var originalTotal = 0;
        multiSelectedProviders.forEach(function (p) {
            originalTotal += p.daily_rate * 1.8;
        });
        var discount = originalTotal * 0.1;
        var finalTotal = originalTotal - discount;

        // Check if all 5 roles are selected — apply extra 5% bonus on the 5th booking
        var isFiveBooking = multiSelectedProviders.length === 5;
        if (isFiveBooking && discountBadge) {
            discountBadge.innerHTML = '<i class="fas fa-tag"></i> 10% + 5% bonus on 5th!';
            // Calculate the 5th provider's extra discount
            var fifthProvider = multiSelectedProviders[4];
            var fifthOriginal = fifthProvider.daily_rate * 1.8;
            var fifthAfter10Percent = fifthOriginal * 0.9;
            var fifthBonus = fifthAfter10Percent * 0.05;
            discount += fifthBonus;
            finalTotal -= fifthBonus;
        } else if (discountBadge) {
            discountBadge.innerHTML = '<i class="fas fa-tag"></i> 10% discount applied!';
        }

        totalEl.textContent = Math.round(finalTotal);
        saveEl.textContent = Math.round(discount);
    } else {
        bar.style.display = 'none';
    }
}

function clearMultiSelection() {
    document.querySelectorAll('.provider-checkbox').forEach(function (cb) {
        cb.checked = false;
    });
    multiSelectedProviders = [];
    document.getElementById('multi-booking-bar').style.display = 'none';
}

function openMultiBookingModal() {
    if (multiSelectedProviders.length < 2) {
        showToast('Select at least 2 providers', 'error');
        return;
    }

    // Build selected providers list
    var listEl = document.getElementById('multi-selected-list');
    listEl.innerHTML = '';
    var originalTotal = 0;
    var isFiveBooking = multiSelectedProviders.length === 5;

    multiSelectedProviders.forEach(function (p, index) {
        var price = p.daily_rate * 1.8;
        originalTotal += price;
        var item = document.createElement('div');
        item.className = 'multi-selected-item';
        if (isFiveBooking && index === 4) {
            item.className += ' fifth-booking-highlight';
        }
        var roleIcon = p.booked_role === 'dj' ? 'fa-music' :
                       p.booked_role === 'event' ? 'fa-calendar-days' :
                       p.booked_role === 'photographer' ? 'fa-camera' :
                       p.booked_role === 'tent' ? 'fa-campground' : 'fa-utensils';
        var fifthBadge = (isFiveBooking && index === 4) ? ' <span class="fifth-badge"><i class="fas fa-star"></i> +5% bonus</span>' : '';
        item.innerHTML = '<i class="fas ' + roleIcon + '"></i> ' +
                         '<span class="multi-item-name">' + p.username + '</span> ' +
                         '<span class="multi-item-role">' + p.booked_role.charAt(0).toUpperCase() + p.booked_role.slice(1) + '</span>' + fifthBadge + ' ' +
                         '<span class="multi-item-price">KES ' + Math.round(price) + '</span>';
        listEl.appendChild(item);
    });

    var discount = originalTotal * 0.1;
    var fifthBonus = 0;
    if (isFiveBooking) {
        var fifthProvider = multiSelectedProviders[4];
        var fifthOriginal = fifthProvider.daily_rate * 1.8;
        var fifthAfter10Percent = fifthOriginal * 0.9;
        fifthBonus = fifthAfter10Percent * 0.05;
    }
    var totalDiscount = discount + fifthBonus;
    var finalTotal = originalTotal - totalDiscount;

    document.getElementById('multi-original-total').textContent = Math.round(originalTotal);
    document.getElementById('multi-discount-amount').textContent = Math.round(totalDiscount);
    document.getElementById('multi-final-total').textContent = Math.round(finalTotal);

    // Update discount label based on whether 5th bonus applies
    var discountLabel = document.getElementById('multi-discount-label');
    var fifthBonusRow = document.getElementById('multi-fifth-bonus-row');
    if (isFiveBooking) {
        if (discountLabel) discountLabel.textContent = '10% Multi-Booking Discount';
        if (fifthBonusRow) fifthBonusRow.style.display = 'flex';
        document.getElementById('multi-fifth-bonus-amount').textContent = Math.round(fifthBonus);
    } else {
        if (discountLabel) discountLabel.textContent = '10% Discount';
        if (fifthBonusRow) fifthBonusRow.style.display = 'none';
    }

    // Update discount banner text
    var discountBanner = document.getElementById('multi-discount-banner-text');
    if (discountBanner) {
        if (isFiveBooking) {
            discountBanner.innerHTML = '<strong>10% + 5% Bonus</strong> applied for booking all 5 roles!';
        } else {
            discountBanner.innerHTML = '<strong>10% Discount</strong> applied for booking multiple roles!';
        }
    }

    // Load celebration types
    loadMultiCelebrationTypes();

    // Set minimum date to today
    var today = new Date().toISOString().split('T')[0];
    document.getElementById('multi-event-start-date').setAttribute('min', today);
    document.getElementById('multi-event-end-date').setAttribute('min', today);

    document.getElementById('multi-booking-modal').style.display = 'flex';
}

function closeMultiBookingModal() {
    document.getElementById('multi-booking-modal').style.display = 'none';
    document.getElementById('multi-booking-form').reset();
}

var multiCelebrationTypesLoaded = false;

function loadMultiCelebrationTypes() {
    if (multiCelebrationTypesLoaded) return;

    fetch('/api/celebration-types')
    .then(function (response) {
        return response.json();
    })
    .then(function (data) {
        if (data.success) {
            var select = document.getElementById('multi-celebration-type');
            select.innerHTML = '<option value="">Select a celebration type</option>';
            data.types.forEach(function (type) {
                var option = document.createElement('option');
                option.value = type.name;
                option.textContent = type.name;
                select.appendChild(option);
            });
            multiCelebrationTypesLoaded = true;
        }
    })
    .catch(function (error) {
        console.error('Failed to load celebration types:', error);
    });
}

function submitMultiBooking(event) {
    event.preventDefault();

    var celebrationType = document.getElementById('multi-celebration-type').value;
    var celebrationTitle = document.getElementById('multi-celebration-title').value.trim();
    var venueLocation = document.getElementById('multi-venue-location').value.trim();
    var eventStartDate = document.getElementById('multi-event-start-date').value;
    var eventEndDate = document.getElementById('multi-event-end-date').value;
    var startTime = document.getElementById('multi-start-time').value;
    var endTime = document.getElementById('multi-end-time').value;
    var attendeesCount = document.getElementById('multi-attendees-count').value;

    // Validate
    if (!celebrationType) {
        showToast('Please select a celebration type', 'error');
        return;
    }
    if (!celebrationTitle) {
        showToast('Please enter a celebration title', 'error');
        return;
    }
    if (!venueLocation) {
        showToast('Please enter a venue location', 'error');
        return;
    }
    if (!eventStartDate) {
        showToast('Please select an event start date', 'error');
        return;
    }
    if (!startTime || !endTime) {
        showToast('Please select start and end times', 'error');
        return;
    }
    if (endTime <= startTime) {
        showToast('End time must be after start time', 'error');
        return;
    }
    if (!attendeesCount || parseInt(attendeesCount) <= 0) {
        showToast('Please enter the number of attendees', 'error');
        return;
    }
    if (eventEndDate && eventEndDate < eventStartDate) {
        showToast('Event end date must be after start date', 'error');
        return;
    }

    fetch('/api/book/multi', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            providers: multiSelectedProviders,
            event_start_date: eventStartDate,
            event_end_date: eventEndDate || null,
            celebration_type: celebrationType,
            celebration_title: celebrationTitle,
            venue_location: venueLocation,
            start_time: startTime,
            end_time: endTime,
            attendees_count: parseInt(attendeesCount)
        })
    })
    .then(function (response) {
        return response.json().then(function (data) {
            if (!response.ok) {
                throw new Error(data.message || 'Multi-booking failed');
            }
            return data;
        });
    })
    .then(function (data) {
        if (data.success) {
            closeMultiBookingModal();
            clearMultiSelection();
            if (data.is_five_booking) {
                showToast('Multi-booking sent with 10% + 5% bonus discount! Save KES ' + Math.round(data.discount_amount), 'success');
            } else {
                showToast('Multi-booking sent with 10% discount! Save KES ' + Math.round(data.discount_amount), 'success');
            }
            setTimeout(function () {
                location.reload();
            }, 2000);
        } else {
            showToast(data.message || 'Multi-booking failed', 'error');
        }
    })
    .catch(function (error) {
        showToast(error.message || 'Something went wrong', 'error');
    });
}

/* =========================
   CLOSE MODALS ON OVERLAY CLICK
========================= */

document.addEventListener('click', function (e) {
    if (e.target.id === 'booking-modal') {
        closeBookingModal();
    }
    if (e.target.id === 'reject-modal') {
        closeRejectModal();
    }
    if (e.target.id === 'multi-booking-modal') {
        closeMultiBookingModal();
    }
});
