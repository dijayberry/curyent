/**
 * CURYENT Social Pages
 * Friends page and Review page JavaScript
 */

(function() {
    'use strict';

    // =========================
    // Detect which page we're on
    // =========================
    const isFriendsPage = document.querySelector('.tabs-container') !== null;
    const isReviewPage = document.querySelector('.review-profile-section') !== null;

    if (isFriendsPage) {
        initFriendsPage();
    }
    if (isReviewPage) {
        initReviewPage();
    }

    // =========================
    // Friends Page
    // =========================
    function initFriendsPage() {
        let currentTab = 'friends';
        let searchTimeout = null;

        // Load initial data
        loadTab('friends');
        loadCounts();

        // Tab switching
        document.querySelectorAll('.tab-btn').forEach(function(btn) {
            btn.addEventListener('click', function() {
                const tab = this.getAttribute('data-tab');
                switchTab(tab);
            });
        });

        // Search input
        const searchInput = document.getElementById('search-input');
        const searchClear = document.getElementById('search-clear');

        if (searchInput) {
            searchInput.addEventListener('input', function() {
                const query = this.value.trim();
                searchClear.style.display = query ? 'block' : 'none';

                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(function() {
                    if (currentTab === 'find') {
                        loadFindUsers(query);
                    } else {
                        // Filter current list
                        filterUsers(query);
                    }
                }, 300);
            });
        }

        if (searchClear) {
            searchClear.addEventListener('click', function() {
                searchInput.value = '';
                this.style.display = 'none';
                if (currentTab === 'find') {
                    loadFindUsers('');
                } else {
                    filterUsers('');
                }
            });
        }

        // Expose switchTab globally for the empty state button
        window.switchTab = function(tab) {
            switchTab(tab);
        };

        function switchTab(tab) {
            currentTab = tab;

            // Update active tab button
            document.querySelectorAll('.tab-btn').forEach(function(btn) {
                btn.classList.toggle('active', btn.getAttribute('data-tab') === tab);
            });

            // Clear search
            if (searchInput) searchInput.value = '';
            if (searchClear) searchClear.style.display = 'none';

            loadTab(tab);
        }

        function loadTab(tab) {
            const userList = document.getElementById('user-list');
            const emptyState = document.getElementById('empty-state');

            // Show loading
            userList.innerHTML = '<div class="loading-spinner" id="loading"><i class="fas fa-spinner fa-spin"></i><p>Loading...</p></div>';
            emptyState.style.display = 'none';

            let url = '';
            switch (tab) {
                case 'friends':
                    url = '/api/friends/mutual';
                    break;
                case 'following':
                    url = '/api/friends/following';
                    break;
                case 'followers':
                    url = '/api/friends/followers';
                    break;
                case 'find':
                    loadFindUsers('');
                    return;
            }

            fetch(url)
                .then(function(response) { return response.json(); })
                .then(function(data) {
                    if (data.success) {
                        renderUsers(data.users, tab);
                    } else {
                        userList.innerHTML = '';
                        emptyState.style.display = 'block';
                    }
                })
                .catch(function() {
                    userList.innerHTML = '<div class="empty-state"><i class="fas fa-exclamation-triangle"></i><h3>Error loading data</h3><p>Please try again.</p></div>';
                });
        }

        function loadFindUsers(query) {
            const userList = document.getElementById('user-list');
            const emptyState = document.getElementById('empty-state');

            userList.innerHTML = '<div class="loading-spinner" id="loading"><i class="fas fa-spinner fa-spin"></i><p>Searching...</p></div>';
            emptyState.style.display = 'none';

            let url = '/api/friends/find';
            if (query) {
                url += '?q=' + encodeURIComponent(query);
            }

            fetch(url)
                .then(function(response) { return response.json(); })
                .then(function(data) {
                    if (data.success) {
                        renderUsers(data.users, 'find');
                    } else {
                        userList.innerHTML = '';
                        emptyState.style.display = 'block';
                    }
                })
                .catch(function() {
                    userList.innerHTML = '<div class="empty-state"><i class="fas fa-exclamation-triangle"></i><h3>Error loading data</h3><p>Please try again.</p></div>';
                });
        }

        function renderUsers(users, tab) {
            const userList = document.getElementById('user-list');
            const emptyState = document.getElementById('empty-state');

            if (!users || users.length === 0) {
                userList.innerHTML = '';
                if (tab !== 'find') {
                    emptyState.style.display = 'block';
                } else {
                    userList.innerHTML = '<div class="empty-state"><i class="fas fa-search"></i><h3>No users found</h3><p>Try a different search term.</p></div>';
                }
                return;
            }

            emptyState.style.display = 'none';
            let html = '';

            users.forEach(function(user) {
                const avatarHtml = user.profile_image
                    ? '<img src="' + user.profile_image + '" alt="' + user.username + '">'
                    : '<i class="fas fa-user"></i>';

                const locationHtml = user.location
                    ? '<div class="user-card-location"><i class="fas fa-map-marker-alt"></i> ' + escapeHtml(user.location) + '</div>'
                    : '<div class="user-card-location"><i class="fas fa-map-marker-alt"></i> Unknown</div>';

                let btnHtml = '';
                const relationship = user.relationship || user.status || null;

                if (tab === 'find') {
                    if (relationship === 'friends') {
                        btnHtml = '<button class="btn-action btn-friends" disabled><i class="fas fa-user-check"></i> Friends</button>';
                    } else if (relationship === 'following') {
                        btnHtml = '<button class="btn-action btn-unfollow" data-target-id="' + user.id + '"><i class="fas fa-user-minus"></i> Unfollow</button>';
                    } else {
                        btnHtml = '<button class="btn-action btn-follow" data-target-id="' + user.id + '"><i class="fas fa-user-plus"></i> Follow</button>';
                    }
                } else {
                    // For friends/following/followers tabs
                    if (relationship === 'friends' || user.status === 'friends') {
                        btnHtml = '<button class="btn-action btn-unfriend" data-target-id="' + user.id + '"><i class="fas fa-user-minus"></i> Unfriend</button>';
                    } else if (tab === 'followers') {
                        // Followers tab: show "Follow Back" button
                        btnHtml = '<button class="btn-action btn-follow-back" data-target-id="' + user.id + '"><i class="fas fa-user-plus"></i> Follow Back</button>';
                    } else if (relationship === 'following' || user.status === 'following') {
                        btnHtml = '<button class="btn-action btn-unfollow" data-target-id="' + user.id + '"><i class="fas fa-user-minus"></i> Unfollow</button>';
                    }
                }

                html += '<div class="user-card" data-username="' + escapeHtml(user.username).toLowerCase() + '" data-location="' + escapeHtml(user.location || '').toLowerCase() + '">' +
                    '<div class="user-card-left">' +
                        '<div class="user-card-avatar clickable-profile-pic" data-user-id="' + user.id + '" data-profile-image="' + (user.profile_image || '') + '">' + avatarHtml + '</div>' +
                        '<div class="user-card-info">' +
                            '<div class="user-card-username">' + escapeHtml(user.username) + '</div>' +
                            locationHtml +
                        '</div>' +
                    '</div>' +
                    '<div class="user-card-right">' + btnHtml + '</div>' +
                '</div>';
            });

            userList.innerHTML = html;

            // Attach event listeners
            attachCardListeners();
        }

        function attachCardListeners() {
            // Follow buttons
            document.querySelectorAll('.btn-follow').forEach(function(btn) {
                btn.addEventListener('click', function() {
                    const targetId = this.getAttribute('data-target-id');
                    followUser(targetId, this);
                });
            });

            // Follow Back buttons (in Followers tab)
            document.querySelectorAll('.btn-follow-back').forEach(function(btn) {
                btn.addEventListener('click', function() {
                    const targetId = this.getAttribute('data-target-id');
                    followUser(targetId, this);
                });
            });

            // Unfollow buttons
            document.querySelectorAll('.btn-unfollow').forEach(function(btn) {
                btn.addEventListener('click', function() {
                    const targetId = this.getAttribute('data-target-id');
                    unfollowUser(targetId, this);
                });
            });

            // Unfriend buttons
            document.querySelectorAll('.btn-unfriend').forEach(function(btn) {
                btn.addEventListener('click', function() {
                    const targetId = this.getAttribute('data-target-id');
                    unfollowUser(targetId, this);
                });
            });

            // Clickable profile pictures — navigate to review page
            document.querySelectorAll('.clickable-profile-pic').forEach(function(el) {
                el.addEventListener('click', function(e) {
                    e.preventDefault();
                    const userId = this.getAttribute('data-user-id');
                    if (userId) {
                        window.location.href = '/review/' + userId;
                    }
                });
            });
        }

        function followUser(targetId, btn) {
            const originalHtml = btn.innerHTML;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            btn.disabled = true;

            fetch('/api/friends/follow', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ target_id: targetId })
            })
            .then(function(response) { return response.json(); })
            .then(function(data) {
                if (data.success) {
                    if (data.status === 'friends') {
                        btn.className = 'btn-action btn-friends';
                        btn.innerHTML = '<i class="fas fa-user-check"></i> Friends';
                        btn.disabled = true;
                        showToast('🎉 You are now friends!', 'success');
                    } else {
                        btn.className = 'btn-action btn-unfollow';
                        btn.innerHTML = '<i class="fas fa-user-minus"></i> Unfollow';
                        btn.disabled = false;
                        btn.setAttribute('data-target-id', targetId);
                        btn.removeEventListener('click', arguments.callee);
                        btn.addEventListener('click', function() {
                            unfollowUser(targetId, btn);
                        });
                        showToast('Now following!', 'success');
                    }
                    loadCounts();
                } else {
                    btn.innerHTML = originalHtml;
                    btn.disabled = false;
                    showToast(data.message || 'Failed to follow', 'error');
                }
            })
            .catch(function() {
                btn.innerHTML = originalHtml;
                btn.disabled = false;
                showToast('Network error', 'error');
            });
        }

        function unfollowUser(targetId, btn) {
            const originalHtml = btn.innerHTML;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            btn.disabled = true;

            fetch('/api/friends/unfollow', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ target_id: targetId })
            })
            .then(function(response) { return response.json(); })
            .then(function(data) {
                if (data.success) {
                    // Remove the card from the list
                    const card = btn.closest('.user-card');
                    if (card) {
                        card.style.opacity = '0';
                        card.style.transform = 'translateX(-20px)';
                        card.style.transition = 'all 0.3s ease';
                        setTimeout(function() {
                            card.remove();
                            checkEmpty();
                        }, 300);
                    }
                    loadCounts();
                } else {
                    btn.innerHTML = originalHtml;
                    btn.disabled = false;
                    showToast(data.message || 'Failed to unfollow', 'error');
                }
            })
            .catch(function() {
                btn.innerHTML = originalHtml;
                btn.disabled = false;
                showToast('Network error', 'error');
            });
        }

        function checkEmpty() {
            const cards = document.querySelectorAll('.user-card');
            if (cards.length === 0 && currentTab !== 'find') {
                document.getElementById('user-list').innerHTML = '';
                document.getElementById('empty-state').style.display = 'block';
            }
        }

        function filterUsers(query) {
            const cards = document.querySelectorAll('.user-card');
            let visibleCount = 0;

            cards.forEach(function(card) {
                const username = card.getAttribute('data-username') || '';
                const location = card.getAttribute('data-location') || '';
                const match = !query || username.includes(query.toLowerCase()) || location.includes(query.toLowerCase());
                card.style.display = match ? 'flex' : 'none';
                if (match) visibleCount++;
            });

            const emptyState = document.getElementById('empty-state');
            if (visibleCount === 0 && query) {
                document.getElementById('user-list').innerHTML = '<div class="empty-state"><i class="fas fa-search"></i><h3>No matches</h3><p>Try a different search term.</p></div>';
            }
        }

        function loadCounts() {
            fetch('/api/friends/count')
                .then(function(response) { return response.json(); })
                .then(function(data) {
                    if (data.success) {
                        const friendsCount = document.getElementById('friends-count');
                        const followingCount = document.getElementById('following-count');
                        const followersCount = document.getElementById('followers-count');

                        if (friendsCount) friendsCount.textContent = data.friends;
                        if (followingCount) followingCount.textContent = data.following;
                        if (followersCount) followersCount.textContent = data.followers;
                    }
                })
                .catch(function() { /* Silent fail for counts */ });
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        function showToast(message, type) {
            // Simple toast notification
            const toast = document.createElement('div');
            toast.style.cssText = 'position:fixed;bottom:20px;right:20px;padding:12px 20px;border-radius:8px;color:#fff;font-size:14px;z-index:10000;animation:fadeIn 0.3s ease;';
            if (type === 'error') {
                toast.style.background = 'rgba(255,100,100,0.9)';
            } else if (type === 'success') {
                toast.style.background = 'rgba(52,211,153,0.9)';
            } else {
                toast.style.background = 'rgba(201,160,255,0.9)';
            }
            toast.textContent = message;
            document.body.appendChild(toast);
            setTimeout(function() {
                toast.style.opacity = '0';
                toast.style.transition = 'opacity 0.3s ease';
                setTimeout(function() { toast.remove(); }, 300);
            }, 3000);
        }
    }

    // =========================
    // Review Page
    // =========================
    function initReviewPage() {
        // Tab switching
        document.querySelectorAll('.review-tab-btn').forEach(function(btn) {
            btn.addEventListener('click', function() {
                const tab = this.getAttribute('data-tab');

                // Update active tab
                document.querySelectorAll('.review-tab-btn').forEach(function(b) {
                    b.classList.remove('active');
                });
                this.classList.add('active');

                // Show/hide content
                const postsContent = document.getElementById('posts-content');
                const rankingContent = document.getElementById('ranking-content');

                if (tab === 'posts') {
                    postsContent.style.display = 'block';
                    rankingContent.style.display = 'none';
                } else {
                    postsContent.style.display = 'none';
                    rankingContent.style.display = 'block';
                }
            });
        });

        // Follow/Unfollow button
        const actionBtn = document.getElementById('review-action-btn');
        if (actionBtn) {
            actionBtn.addEventListener('click', function() {
                const targetId = this.getAttribute('data-target-id');
                const currentRel = window.currentRelationship || '';

                if (currentRel === 'friends' || currentRel === 'following') {
                    // Unfollow/Unfriend
                    unfollowReviewUser(targetId, this);
                } else {
                    // Follow
                    followReviewUser(targetId, this);
                }
            });
        }

        // Clickable profile pictures — show popup or navigate
        document.querySelectorAll('.clickable-profile-pic').forEach(function(el) {
            el.addEventListener('click', function(e) {
                e.preventDefault();
                const userId = this.getAttribute('data-user-id');
                const profileImage = window.reviewedUserProfileImage || '';

                // If it's the review page's own profile picture, show popup
                if (userId == window.reviewedUserId && profileImage) {
                    showImagePopup(profileImage);
                } else {
                    // Navigate to review page
                    window.location.href = '/review/' + userId;
                }
            });
        });

        // Image popup
        const popup = document.getElementById('image-popup');
        const popupClose = document.getElementById('image-popup-close');
        const popupOverlay = popup ? popup.querySelector('.image-popup-overlay') : null;

        if (popupClose) {
            popupClose.addEventListener('click', function() {
                hideImagePopup();
            });
        }

        if (popupOverlay) {
            popupOverlay.addEventListener('click', function() {
                hideImagePopup();
            });
        }

        // ESC key to close popup
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                hideImagePopup();
            }
        });

        function followReviewUser(targetId, btn) {
            const originalHtml = btn.innerHTML;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            btn.disabled = true;

            fetch('/api/friends/follow', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ target_id: targetId })
            })
            .then(function(response) { return response.json(); })
            .then(function(data) {
                if (data.success) {
                    if (data.status === 'friends') {
                        btn.className = 'btn-review-action unfriend';
                        btn.innerHTML = '<i class="fas fa-user-minus"></i> Unfriend';
                    } else {
                        btn.className = 'btn-review-action unfollow';
                        btn.innerHTML = '<i class="fas fa-user-minus"></i> Unfollow';
                    }
                    window.currentRelationship = data.status;
                    btn.disabled = false;
                } else {
                    btn.innerHTML = originalHtml;
                    btn.disabled = false;
                }
            })
            .catch(function() {
                btn.innerHTML = originalHtml;
                btn.disabled = false;
            });
        }

        function unfollowReviewUser(targetId, btn) {
            const originalHtml = btn.innerHTML;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            btn.disabled = true;

            fetch('/api/friends/unfollow', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ target_id: targetId })
            })
            .then(function(response) { return response.json(); })
            .then(function(data) {
                if (data.success) {
                    btn.className = 'btn-review-action follow';
                    btn.innerHTML = '<i class="fas fa-user-plus"></i> Follow';
                    window.currentRelationship = '';
                    btn.disabled = false;
                } else {
                    btn.innerHTML = originalHtml;
                    btn.disabled = false;
                }
            })
            .catch(function() {
                btn.innerHTML = originalHtml;
                btn.disabled = false;
            });
        }
    }

    // =========================
    // Image Popup (shared)
    // =========================
    function showImagePopup(imageSrc) {
        const popup = document.getElementById('image-popup');
        const popupImage = document.getElementById('popup-image');

        if (popup && popupImage) {
            popupImage.src = imageSrc;
            popup.classList.add('active');
            document.body.style.overflow = 'hidden';
        }
    }

    function hideImagePopup() {
        const popup = document.getElementById('image-popup');
        if (popup) {
            popup.classList.remove('active');
            document.body.style.overflow = '';
        }
    }

    // Make popup functions available globally
    window.showImagePopup = showImagePopup;
    window.hideImagePopup = hideImagePopup;

})();
