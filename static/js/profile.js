/* =========================
   TAB SWITCHING
========================= */

document.addEventListener('DOMContentLoaded', function () {
    var tabButtons = document.querySelectorAll('.profile-tab-btn');
    var tabPanes = document.querySelectorAll('.profile-tab-pane');

    tabButtons.forEach(function (btn) {
        btn.addEventListener('click', function () {
            var targetTab = this.getAttribute('data-tab');

            // Remove active class from all buttons and panes
            tabButtons.forEach(function (b) { 
                b.classList.remove('active'); 
                b.setAttribute('aria-selected', 'false');
            });
            tabPanes.forEach(function (p) { p.classList.remove('active'); });

            // Add active class to clicked button and corresponding pane
            this.classList.add('active');
            this.setAttribute('aria-selected', 'true');
            var targetPane = document.getElementById('tab-' + targetTab);
            if (targetPane) {
                targetPane.classList.add('active');
            }

            // Render chart when switching to ranking tab
            if (targetTab === 'ranking') {
                renderOrdersChart();
            }
        });
    });

    // Initialize profile edit functionality
    initProfileEdit();

    // Initialize header edit profile button
    initHeaderEditButton();

    // Initialize profile image upload
    initProfileImageUpload();

    // Render chart if ranking tab is active on load
    var activeTab = document.querySelector('.profile-tab-btn.active');
    if (activeTab && activeTab.getAttribute('data-tab') === 'ranking') {
        renderOrdersChart();
    }
});


/* =========================
   HEADER EDIT BUTTON
========================= */

function initHeaderEditButton() {
    var btnHeaderEdit = document.getElementById('btn-edit-profile');
    
    if (btnHeaderEdit) {
        btnHeaderEdit.addEventListener('click', function () {
            // Switch to Personal Details tab
            var personalTab = document.querySelector('.profile-tab-btn[data-tab="personal"]');
            if (personalTab) {
                personalTab.click();
            }
            
            // Trigger the edit button in the Personal Details section
            setTimeout(function () {
                var btnEdit = document.getElementById('btn-edit');
                if (btnEdit) {
                    btnEdit.click();
                }
            }, 100);
        });
    }
}


/* =========================
   PROFILE EDIT FUNCTIONALITY
========================= */

function initProfileEdit() {
    var btnEdit = document.getElementById('btn-edit');
    var btnSave = document.getElementById('btn-save');
    var btnCancel = document.getElementById('btn-cancel');
    var formActions = document.getElementById('form-actions');
    var inputs = document.querySelectorAll('.profile-form .form-input:not([disabled])');

    // Store original values
    var originalValues = {};

    if (btnEdit) {
        btnEdit.addEventListener('click', function () {
            // Save original values
            inputs.forEach(function (input) {
                originalValues[input.id] = input.value;
            });

            // Enable inputs and highlight editable fields
            inputs.forEach(function (input) {
                if (input.id !== 'role' && input.id !== 'created_at') {
                    input.removeAttribute('readonly');
                    input.classList.add('editing');
                }
            });

            // Show save/cancel buttons
            if (formActions) {
                formActions.style.display = 'flex';
            }

            // Hide edit button
            btnEdit.style.display = 'none';

            // Focus on first editable field
            var firstEditable = document.querySelector('.form-input.editing');
            if (firstEditable) {
                firstEditable.focus();
            }
        });
    }

    if (btnSave) {
        btnSave.addEventListener('click', function () {
            // Validate email format
            var emailInput = document.getElementById('email');
            if (emailInput && emailInput.value) {
                var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(emailInput.value)) {
                    showToast('Please enter a valid email address');
                    emailInput.focus();
                    return;
                }
            }

            // Validate phone format (should start with +254)
            var phoneInput = document.getElementById('phone');
            if (phoneInput && phoneInput.value) {
                var phoneRegex = /^\+2547\d{8}$/;
                if (!phoneRegex.test(phoneInput.value)) {
                    showToast('Phone number must be in format +2547xxxxxxxx');
                    phoneInput.focus();
                    return;
                }
            }

            // Show loading state
            btnSave.classList.add('loading');
            btnSave.disabled = true;

            // Collect form data
            var data = {};
            inputs.forEach(function (input) {
                if (input.id !== 'role' && input.id !== 'created_at') {
                    data[input.id] = input.value;
                }
            });

            // Send update request
            fetch('/api/profile', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
            .then(function (response) { 
                if (!response.ok) throw new Error('Network response was not ok');
                return response.json(); 
            })
            .then(function (result) {
                if (result.success) {
                    showToast('Profile updated successfully!');
                    // Reload page to show updated data
                    setTimeout(function () {
                        window.location.reload();
                    }, 1000);
                } else {
                    showToast(result.message || 'Failed to update profile');
                    btnSave.classList.remove('loading');
                    btnSave.disabled = false;
                }
            })
            .catch(function (error) {
                console.error('Error:', error);
                showToast('Error updating profile. Please try again.');
                btnSave.classList.remove('loading');
                btnSave.disabled = false;
            });
        });
    }

    if (btnCancel) {
        btnCancel.addEventListener('click', function () {
            // Restore original values
            inputs.forEach(function (input) {
                input.value = originalValues[input.id] || '';
                input.setAttribute('readonly', true);
                input.classList.remove('editing');
            });

            // Hide save/cancel buttons
            if (formActions) {
                formActions.style.display = 'none';
            }

            // Show edit button
            btnEdit.style.display = 'inline-flex';
        });
    }
}


/* =========================
   ORDERS CHART (Chart.js)
========================= */

var ordersChartInstance = null;

function renderOrdersChart() {
    var canvas = document.getElementById('ordersChart');
    if (!canvas) return;

    // Destroy existing chart if any
    if (ordersChartInstance) {
        ordersChartInstance.destroy();
    }

    // Get stats data from global variable
    var stats = typeof statsData !== 'undefined' ? statsData : {};
    var ordersReceived = stats.orders_received || {};
    var ordersMade = stats.orders_made || {};

    var labels = ['Pending', 'Accepted', 'Declined'];
    var receivedData = [
        ordersReceived['pending'] || 0,
        ordersReceived['accepted'] || 0,
        ordersReceived['declined'] || 0
    ];
    var madeData = [
        ordersMade['pending'] || 0,
        ordersMade['accepted'] || 0,
        ordersMade['declined'] || 0
    ];

    var ctx = canvas.getContext('2d');
    ordersChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Orders for Me',
                    data: receivedData,
                    backgroundColor: 'rgba(107, 63, 160, 0.7)',
                    borderColor: 'rgba(201, 160, 255, 0.8)',
                    borderWidth: 2,
                    borderRadius: 8
                },
                {
                    label: 'Orders I Made',
                    data: madeData,
                    backgroundColor: 'rgba(33, 150, 243, 0.7)',
                    borderColor: 'rgba(100, 181, 246, 0.8)',
                    borderWidth: 2,
                    borderRadius: 8
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: '#b39ddb',
                        font: {
                            size: 14,
                            weight: '600'
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(26, 15, 46, 0.95)',
                    titleColor: '#ffffff',
                    bodyColor: '#b39ddb',
                    borderColor: 'rgba(201, 160, 255, 0.3)',
                    borderWidth: 1,
                    cornerRadius: 8,
                    padding: 12
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: '#9e9e9e',
                        stepSize: 1
                    },
                    grid: {
                        color: 'rgba(201, 160, 255, 0.1)'
                    }
                },
                x: {
                    ticks: {
                        color: '#9e9e9e'
                    },
                    grid: {
                        color: 'rgba(201, 160, 255, 0.1)'
                    }
                }
            }
        }
    });
}


/* =========================
   ACCEPT / DECLINE BOOKING
========================= */

function acceptBooking(bookingId) {
    if (!confirm('Are you sure you want to accept this booking?')) {
        return;
    }

    // Find and disable the accept button
    var buttons = document.querySelectorAll('.btn-accept');
    buttons.forEach(function(btn) {
        if (btn.onclick && btn.onclick.toString().indexOf(bookingId) !== -1) {
            btn.disabled = true;
            btn.classList.add('loading');
        }
    });

    fetch('/api/booking/accept/' + bookingId, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(function (response) { 
        if (!response.ok) throw new Error('Network response was not ok');
        return response.json(); 
    })
    .then(function (result) {
        if (result.success) {
            showToast('Booking accepted successfully!');
            setTimeout(function () {
                window.location.reload();
            }, 1000);
        } else {
            showToast(result.message || 'Failed to accept booking');
            buttons.forEach(function(btn) {
                btn.disabled = false;
                btn.classList.remove('loading');
            });
        }
    })
    .catch(function (error) {
        console.error('Error:', error);
        showToast('Error accepting booking. Please try again.');
        buttons.forEach(function(btn) {
            btn.disabled = false;
            btn.classList.remove('loading');
        });
    });
}

function declineBooking(bookingId) {
    if (!confirm('Are you sure you want to decline this booking?')) {
        return;
    }

    // Find and disable the decline button
    var buttons = document.querySelectorAll('.btn-decline');
    buttons.forEach(function(btn) {
        if (btn.onclick && btn.onclick.toString().indexOf(bookingId) !== -1) {
            btn.disabled = true;
            btn.classList.add('loading');
        }
    });

    fetch('/api/booking/decline/' + bookingId, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(function (response) { 
        if (!response.ok) throw new Error('Network response was not ok');
        return response.json(); 
    })
    .then(function (result) {
        if (result.success) {
            showToast('Booking declined');
            setTimeout(function () {
                window.location.reload();
            }, 1000);
        } else {
            showToast(result.message || 'Failed to decline booking');
            buttons.forEach(function(btn) {
                btn.disabled = false;
                btn.classList.remove('loading');
            });
        }
    })
    .catch(function (error) {
        console.error('Error:', error);
        showToast('Error declining booking. Please try again.');
        buttons.forEach(function(btn) {
            btn.disabled = false;
            btn.classList.remove('loading');
        });
    });
}


/* =========================
   TOAST NOTIFICATION
========================= */

function showToast(message) {
    var toast = document.getElementById('toast');
    var toastMessage = document.getElementById('toast-message');

    if (toast && toastMessage) {
        toastMessage.textContent = message;
        toast.classList.add('show');

        setTimeout(function () {
            toast.classList.remove('show');
        }, 3000);
    }
}


/* =========================
   POSTS FUNCTIONALITY
========================= */

var selectedPostFile = null;

function initPosts() {
    var fileInput = document.getElementById('post-image-input');
    var uploadArea = document.getElementById('post-upload-area');
    var previewImg = document.getElementById('post-preview');
    var captionInput = document.getElementById('post-caption');
    var submitBtn = document.getElementById('btn-post-submit');
    var cancelBtn = document.getElementById('btn-post-cancel');
    var modal = document.getElementById('image-modal');
    var modalClose = document.getElementById('image-modal-close');
    var modalImage = document.getElementById('image-modal-image');
    var modalCaption = document.getElementById('image-modal-caption');

    // File input change — show preview
    if (fileInput) {
        fileInput.addEventListener('change', function () {
            var file = this.files[0];
            if (!file) return;

            // Validate file type
            if (!file.type.startsWith('image/')) {
                showToast('Please select an image file');
                this.value = '';
                return;
            }

            selectedPostFile = file;
            var reader = new FileReader();
            reader.onload = function (e) {
                previewImg.src = e.target.result;
                uploadArea.style.display = 'block';
            };
            reader.readAsDataURL(file);
        });
    }

    // Cancel upload
    if (cancelBtn) {
        cancelBtn.addEventListener('click', function () {
            resetUploadArea();
        });
    }

    // Submit post
    if (submitBtn) {
        submitBtn.addEventListener('click', function () {
            if (!selectedPostFile) return;

            var caption = captionInput ? captionInput.value.trim() : '';
            var formData = new FormData();
            formData.append('image', selectedPostFile);
            formData.append('caption', caption);

            // Show loading state
            submitBtn.disabled = true;
            submitBtn.classList.add('loading');

            // Show progress bar
            var progressContainer = document.getElementById('upload-progress');
            var progressBar = document.getElementById('upload-progress-bar');
            if (progressContainer) {
                progressContainer.classList.add('active');
            }
            
            // Simulate progress animation (since fetch doesn't provide upload progress)
            var progressInterval = setInterval(function() {
                if (progressBar) {
                    var currentWidth = parseInt(progressBar.style.width) || 0;
                    if (currentWidth < 90) {
                        progressBar.style.width = (currentWidth + 10) + '%';
                    }
                }
            }, 200);

            fetch('/api/profile/posts', {
                method: 'POST',
                body: formData
            })
            .then(function (response) { 
                if (!response.ok) throw new Error('Network response was not ok');
                return response.json(); 
            })
            .then(function (result) {
                clearInterval(progressInterval);
                if (progressBar) progressBar.style.width = '100%';
                
                if (result.success) {
                    showToast('Photo posted successfully!');
                    resetUploadArea();
                    // Reload to show new post
                    setTimeout(function () {
                        window.location.reload();
                    }, 1000);
                } else {
                    showToast(result.message || 'Failed to upload photo');
                    submitBtn.disabled = false;
                    submitBtn.classList.remove('loading');
                    if (progressContainer) progressContainer.classList.remove('active');
                    if (progressBar) progressBar.style.width = '0%';
                }
            })
            .catch(function (error) {
                clearInterval(progressInterval);
                console.error('Error:', error);
                showToast('Error uploading photo. Please try again.');
                submitBtn.disabled = false;
                submitBtn.classList.remove('loading');
                if (progressContainer) progressContainer.classList.remove('active');
                if (progressBar) progressBar.style.width = '0%';
            });
        });
    }

    // Image click — open modal
    document.addEventListener('click', function (e) {
        var postImage = e.target.closest('.post-image');
        if (postImage) {
            var postItem = postImage.closest('.post-item');
            var src = postImage.getAttribute('src');
            var caption = '';
            var captionEl = postItem.querySelector('.post-caption-overlay p');
            if (captionEl) {
                caption = captionEl.textContent;
            }

            modalImage.src = src;
            modalCaption.textContent = caption;
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
        }
    });

    // Close modal
    if (modalClose) {
        modalClose.addEventListener('click', function () {
            closeModal();
        });
    }

    // Close modal on background click
    if (modal) {
        modal.addEventListener('click', function (e) {
            if (e.target === modal) {
                closeModal();
            }
        });
    }

    // Close modal on Escape key
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && modal && modal.classList.contains('active')) {
            closeModal();
        }
    });
}

function resetUploadArea() {
    var uploadArea = document.getElementById('post-upload-area');
    var previewImg = document.getElementById('post-preview');
    var captionInput = document.getElementById('post-caption');
    var fileInput = document.getElementById('post-image-input');

    if (uploadArea) uploadArea.style.display = 'none';
    if (previewImg) previewImg.src = '';
    if (captionInput) captionInput.value = '';
    if (fileInput) fileInput.value = '';
    selectedPostFile = null;
}

function closeModal() {
    var modal = document.getElementById('image-modal');
    var modalImage = document.getElementById('image-modal-image');
    var modalCaption = document.getElementById('image-modal-caption');

    if (modal) {
        modal.classList.remove('active');
        modalImage.src = '';
        modalCaption.textContent = '';
        document.body.style.overflow = '';
    }
}

function deletePost(postId) {
    event.stopPropagation();
    if (!confirm('Are you sure you want to delete this post?')) {
        return;
    }

    fetch('/api/profile/posts/' + postId, {
        method: 'DELETE'
    })
    .then(function (response) { return response.json(); })
    .then(function (result) {
        if (result.success) {
            showToast('Post deleted');
            // Remove post from grid
            var postItem = document.querySelector('.post-item[data-post-id="' + postId + '"]');
            if (postItem) {
                postItem.remove();
            }
            // Show empty state if no posts left
            var postsGrid = document.getElementById('posts-grid');
            var emptyState = document.getElementById('posts-empty-state');
            if (postsGrid && postsGrid.children.length === 0) {
                if (emptyState) emptyState.style.display = 'block';
            }
        } else {
            showToast(result.message || 'Failed to delete post');
        }
    })
    .catch(function (error) {
        console.error('Error:', error);
        showToast('Error deleting post');
    });
}

// Initialize posts on DOM ready
document.addEventListener('DOMContentLoaded', function () {
    initPosts();
    initClickableProfilePic();
});

/* =========================
   CLICKABLE PROFILE PICTURE
   Shows full-screen popup on profile page
========================= */

function initClickableProfilePic() {
    var clickablePics = document.querySelectorAll('.clickable-profile-pic');
    var modal = document.getElementById('image-modal');
    var modalImage = document.getElementById('image-modal-image');
    var modalClose = document.getElementById('image-modal-close');

    clickablePics.forEach(function(el) {
        el.style.cursor = 'pointer';
        el.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            var profileImage = this.getAttribute('data-profile-image') || '';
            if (profileImage && modal && modalImage) {
                modalImage.src = profileImage;
                modal.classList.add('active');
                document.body.style.overflow = 'hidden';
            }
        });
    });

    // Close modal
    if (modalClose) {
        modalClose.addEventListener('click', function() {
            closeModal();
        });
    }

    // Close on overlay click
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeModal();
            }
        });
    }
}


/* =========================
   PROFILE IMAGE UPLOAD
========================= */

function initProfileImageUpload() {
    var btnUpload = document.getElementById('btn-upload-image');
    var fileInput = document.getElementById('profile-image-input');
    var preview = document.getElementById('profile-image-preview');
    var img = document.getElementById('profile-image-img');

    // Click on preview to trigger file input
    if (preview) {
        preview.addEventListener('click', function () {
            if (fileInput) fileInput.click();
        });
    }

    // Click on upload button to trigger file input
    if (btnUpload) {
        btnUpload.addEventListener('click', function () {
            if (fileInput) fileInput.click();
        });
    }

    // Handle file selection
    if (fileInput) {
        fileInput.addEventListener('change', function () {
            if (this.files && this.files[0]) {
                var file = this.files[0];

                // Validate file type
                var allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp'];
                if (allowedTypes.indexOf(file.type) === -1) {
                    showToast('Please select a valid image file');
                    this.value = '';
                    return;
                }

                // Preview the image locally
                var reader = new FileReader();
                reader.onload = function (e) {
                    if (img) img.src = e.target.result;
                };
                reader.readAsDataURL(file);

                // Upload the image
                uploadProfileImage(file);
            }
        });
    }
}

function uploadProfileImage(file) {
    var formData = new FormData();
    formData.append('profile_image', file);

    var btnUpload = document.getElementById('btn-upload-image');
    if (btnUpload) {
        btnUpload.disabled = true;
        btnUpload.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Uploading...';
    }

    fetch('/api/profile/image', {
        method: 'POST',
        body: formData
    })
    .then(function (response) { return response.json(); })
    .then(function (result) {
        if (result.success) {
            showToast('Profile photo updated!');
            // Reload page to update header image
            setTimeout(function () {
                window.location.reload();
            }, 1000);
        } else {
            showToast(result.message || 'Failed to upload photo');
            if (btnUpload) {
                btnUpload.disabled = false;
                btnUpload.innerHTML = '<i class="fas fa-camera"></i> Upload Profile Photo';
            }
        }
    })
    .catch(function (error) {
        console.error('Error:', error);
        showToast('Error uploading photo');
        if (btnUpload) {
            btnUpload.disabled = false;
            btnUpload.innerHTML = '<i class="fas fa-camera"></i> Upload Profile Photo';
        }
    });
}
