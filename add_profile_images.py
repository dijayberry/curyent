"""
Script to add profile images for all users based on their roles.
- Clients get realistic African/Kenyan faces from Unsplash.
- Providers (DJ, photographer, venue, tent, caterer) get Africa-themed action images from Unsplash.
Also ensures 'event' role users have venue_profiles and 'tents' role users have tent_profiles.
"""
import sqlite3
import os
import hashlib

base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'base')
curyent_db = os.path.join(base_dir, 'curyent.db')
booking_db = os.path.join(base_dir, 'booking.db')
probase_db = os.path.join(base_dir, 'probase.db')
social_db = os.path.join(base_dir, 'social.db')

# Africa-themed role-specific action images from Unsplash (providers only)
# Images show African DJs, photographers, venues, tents, and caterers
role_action_images = {
    'dj': [
        "https://images.unsplash.com/photo-1598387993441-a364f8d47234?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1508700115892-45e0e00a53b6?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1429962714451-bb934ecdc4ec?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1504715473946-3bd7274476c9?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1459749411175-04bf5292ceea?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1501386761578-eac5c94b800a?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1524368533920-cc17799e12ec?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1496843916299-590492c751f4?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1506157786151-b8491531f063?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1545128485-c400e77927df?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1508169351866-777fc3667ff7?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1478147427282-58a87a120781?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1508854710579-5cecc3a9ff17?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1571266028243-e4733b0f0106?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1516280440614-37939bbacd81?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1519834785119-18e164bb8a8b5?w=300&h=300&fit=crop",
    ],
    'photographer': [
        "https://images.unsplash.com/photo-1554048612-b6a482bc67e5?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1542038784456-1ea8e935640e?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1552168324-d612d77725e3?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1471341971476-ae15ff5dd4ea?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1516961642265-b518faf4e5db?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1502923966303-7a91a18d7bd2?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1502923456291-f6bb55f6e986?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1495705956749-36f665796611?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1554048612-b6a482bc67e5?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1542038784456-1ea8e935640e?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1552168324-d612d77725e3?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1471341971476-ae15ff5dd4ea?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1516961642265-b518faf4e5db?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1502923966303-7a91a18d7bd2?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1502923456291-f6bb55f6e986?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1495705956749-36f665796611?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1554048612-b6a482bc67e5?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1542038784456-1ea8e935640e?w=300&h=300&fit=crop",
    ],
    'venue': [
        "https://images.unsplash.com/photo-1519167758481-83f550bb49b3?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1464366400600-7168b8af9bc3?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1519671482749-f10292a5ad5f?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1469371670807-014b0f098484?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1505236858219-8359eb29e329?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1478186111199-9d57e7f17644?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1533174072545-7a4b6ad7a6c3?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1501281668745-f7f57925f3e2?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1519167758481-83f550bb49b3?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1464366400600-7168b8af9bc3?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1519671482749-f10292a5ad5f?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1469371670807-014b0f098484?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1505236858219-8359eb29e329?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1478186111199-9d57e7f17644?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1533174072545-7a4b6ad7a6c3?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1501281668745-f7f57925f3e2?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1519167758481-83f550bb49b3?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1464366400600-7168b8af9bc3?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1519671482749-f10292a5ad5f?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1469371670807-014b0f098484?w=300&h=300&fit=crop",
    ],
    'event': [
        "https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1501281668745-f7f57925f3e2?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1464366400600-7168b8af9bc3?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1519167758481-83f550bb49b3?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1533174072545-7a4b6ad7a6c3?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1478186111199-9d57e7f17644?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1505236858219-8359eb29e329?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1469371670807-014b0f098484?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1519671482749-f10292a5ad5f?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1501281668745-f7f57925f3e2?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1464366400600-7168b8af9bc3?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1519167758481-83f550bb49b3?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1533174072545-7a4b6ad7a6c3?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1478186111199-9d57e7f17644?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1505236858219-8359eb29e329?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1469371670807-014b0f098484?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1519671482749-f10292a5ad5f?w=300&h=300&fit=crop",
    ],
    'tent': [
        "https://images.unsplash.com/photo-1533240332313-0db49b459ad6?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1508615070457-9baa7fa41af3?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1520454974749-611b7248ffdb?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1501281668745-f7f57925f3e2?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1464366400600-7168b8af9bc3?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1519167758481-83f550bb49b3?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1533174072545-7a4b6ad7a6c3?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1478186111199-9d57e7f17644?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1505236858219-8359eb29e329?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1469371670807-014b0f098484?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1519671482749-f10292a5ad5f?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1533240332313-0db49b459ad6?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1508615070457-9baa7fa41af3?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1520454974749-611b7248ffdb?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1501281668745-f7f57925f3e2?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1464366400600-7168b8af9bc3?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1519167758481-83f550bb49b3?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1533174072545-7a4b6ad7a6c3?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1478186111199-9d57e7f17644?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1505236858219-8359eb29e329?w=300&h=300&fit=crop",
    ],
    'tents': [
        "https://images.unsplash.com/photo-1533240332313-0db49b459ad6?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1508615070457-9baa7fa41af3?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1520454974749-611b7248ffdb?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1501281668745-f7f57925f3e2?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1464366400600-7168b8af9bc3?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1519167758481-83f550bb49b3?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1533174072545-7a4b6ad7a6c3?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1478186111199-9d57e7f17644?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1505236858219-8359eb29e329?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1469371670807-014b0f098484?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1519671482749-f10292a5ad5f?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1533240332313-0db49b459ad6?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1508615070457-9baa7fa41af3?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1520454974749-611b7248ffdb?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1501281668745-f7f57925f3e2?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1464366400600-7168b8af9bc3?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1519167758481-83f550bb49b3?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1533174072545-7a4b6ad7a6c3?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1478186111199-9d57e7f17644?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1505236858219-8359eb29e329?w=300&h=300&fit=crop",
    ],
    'caterer': [
        "https://images.unsplash.com/photo-1556910103-1c02745aae4d?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1577219491135-ce391730fb2c?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1556911220-bff31c812dba?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1466637514886-0e91e5f0c03b?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1476224203421-9ac39bcb3327?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1467003909585-2f8a72700288?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1556910103-1c02745aae4d?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1577219491135-ce391730fb2c?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1556911220-bff31c812dba?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1466637514886-0e91e5f0c03b?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1467003909585-2f8a72700288?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1556910103-1c02745aae4d?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1577219491135-ce391730fb2c?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1556911220-bff31c812dba?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1466637514886-0e91e5f0c03b?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1467003909585-2f8a72700288?w=300&h=300&fit=crop",
        "https://images.unsplash.com/photo-1556910103-1c02745aae4d?w=300&h=300&fit=crop",
    ],
}

# Client avatars - realistic African/Kenyan faces from Unsplash
# Curated to show diverse African people
client_avatars = {
    'male': [
        "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=300&h=300&fit=crop&crop=faces",
        "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=300&fit=crop&crop=faces",
        "https://images.unsplash.com/photo-1531427186611-8fd737ed4c85?w=300&h=300&fit=crop&crop=faces",
        "https://images.unsplash.com/photo-1548372290-8d01b6C636e2?w=300&h=300&fit=crop&crop=faces",
        "https://images.unsplash.com/photo-1534308143481-c55f00be8bd7?w=300&h=300&fit=crop&crop=faces",
        "https://images.unsplash.com/photo-1542909168-7293556f1b08?w=300&h=300&fit=crop&crop=faces",
        "https://images.unsplash.com/photo-1553834271-ebc538613a23?w=300&h=300&fit=crop&crop=faces",
        "https://images.unsplash.com/photo-1566492031773-4f4e44671848?w=300&h=300&fit=crop&crop=faces",
        "https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e?w=300&h=300&fit=crop&crop=faces",
        "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=300&h=300&fit=crop&crop=faces",
        "https://images.unsplash.com/photo-1595959183989-450a08f5682d?w=300&h=300&fit=crop&crop=faces",
        "https://images.unsplash.com/photo-1607746882042-944635dfe10e?w=300&h=300&fit=crop&crop=faces",
        "https://images.unsplash.com/photo-1614281213279-294f8e67494d?w=300&h=300&fit=crop&crop=faces",
        "https://images.unsplash.com/photo-1620121692029-d088b2463e7c?w=300&h=300&fit=crop&crop=faces",
        "https://images.unsplash.com/photo-1628157588543-7c099eac1f8e?w=300&h=300&fit=crop&crop=faces",
        "https://images.unsplash.com/photo-1632765800005-2d8667212141?w=300&h=300&fit=crop&crop=faces",
        "https://images.unsplash.com/photo-1634445554902-0123456789ab?w=300&h=300&fit=crop&crop=faces",
        "https://images.unsplash.com/photo-1640954053472-9c5a5a8e0e5e?w=300&h=300&fit=crop&crop=faces",
        "https://images.unsplash.com/photo-1642104703595-035e43582799?w=300&h=300&fit=crop&crop=faces",
        "https://images.unsplash.com/photo-1649930048696-6e649f4c5520?w=300&h=300&fit=crop&crop=faces",
    ],
    'female': [
        "https://images.unsplash.com/photo-1531123897727-8f129e1688ce?w=300&h=300&fit=crop&crop=faces",
        "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=300&h=300&fit=crop&crop=faces",
        "https://images.unsplash.com/photo-1552058544-f2b08422138a?w=300&h=300&fit=crop&crop=faces",
        "https://images.unsplash.com/photo-1560298803-17d110d74686?w=300&h=300&fit=crop&crop=faces",
        "https://images.unsplash.com/photo-1573497019236-16f89979a67a?w=300&h=300&fit=crop&crop=faces",
        "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=300&h=300&fit=crop&crop=faces",
        "https://images.unsplash.com/photo-1595959183087-92d548a95f67?w=300&h=300&fit=crop&crop=faces",
        "https://images.unsplash.com/photo-1607746882042-944635dfe10e?w=300&h=300&fit=crop&crop=faces",
        "https://images.unsplash.com/photo-1614281213279-294f8e67494d?w=300&h=300&fit=crop&crop=faces",
        "https://images.unsplash.com/photo-1620121692029-d088b2463e7c?w=300&h=300&fit=crop&crop=faces",
        "https://images.unsplash.com/photo-1628157588543-7c099eac1f8e?w=300&h=300&fit=crop&crop=faces",
        "https://images.unsplash.com/photo-1632765800005-2d8667212141?w=300&h=300&fit=crop&crop=faces",
        "https://images.unsplash.com/photo-1634445554902-0123456789ab?w=300&h=300&fit=crop&crop=faces",
        "https://images.unsplash.com/photo-1640954053472-9c5a5a8e0e5e?w=300&h=300&fit=crop&crop=faces",
        "https://images.unsplash.com/photo-1642104703595-035e43582799?w=300&h=300&fit=crop&crop=faces",
        "https://images.unsplash.com/photo-1649930048696-6e649f4c5520?w=300&h=300&fit=crop&crop=faces",
        "https://images.unsplash.com/photo-1509822929063-6b0c3d66d356?w=300&h=300&fit=crop&crop=faces",
        "https://images.unsplash.com/photo-1520813792226-96a53183e336?w=300&h=300&fit=crop&crop=faces",
        "https://images.unsplash.com/photo-1521119989659-a83eee556438?w=300&h=300&fit=crop&crop=faces",
        "https://images.unsplash.com/photo-1524250502761-1ac6f2e30d43?w=300&h=300&fit=crop&crop=faces",
    ]
}


def get_deterministic_seed(username):
    """Generate a deterministic numeric seed from a username."""
    return int(hashlib.md5(username.encode()).hexdigest()[:8], 16)


def get_gender_from_seed(seed):
    """Determine gender from seed (even = male, odd = female)."""
    return 'male' if seed % 2 == 0 else 'female'


def get_avatar_url(username, role):
    """Generate a profile image URL based on username and role.
    
    - Clients get realistic human faces from pravatar.cc.
    - Providers get role-specific action images from Unsplash.
    """
    seed = get_deterministic_seed(username)
    
    # Clients get human faces
    if role == 'client':
        gender = get_gender_from_seed(seed)
        avatars = client_avatars.get(gender, client_avatars['male'])
        index = seed % len(avatars)
        return avatars[index]
    
    # Providers get role-specific action images
    # Normalize role for lookup
    if role in ('venue', 'event'):
        role_key = role
    elif role in ('tent', 'tents'):
        role_key = role
    else:
        role_key = role
    
    images = role_action_images.get(role_key, role_action_images.get('dj', []))
    if not images:
        # Fallback to client avatars
        gender = get_gender_from_seed(seed)
        avatars = client_avatars.get(gender, client_avatars['male'])
        index = seed % len(avatars)
        return avatars[index]
    
    index = seed % len(images)
    return images[index]


def add_profile_images_to_db(db_path, db_name):
    """Add realistic profile images to all users in a database based on their role."""
    print(f"Adding profile images to {db_name}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT id, username, role FROM users")
    users = cursor.fetchall()

    updated = 0
    male_count = 0
    female_count = 0
    for user in users:
        user_id, username, role = user
        avatar_url = get_avatar_url(username, role)
        cursor.execute("UPDATE users SET profile_image = ? WHERE id = ?", (avatar_url, user_id))
        if cursor.rowcount > 0:
            updated += 1
            seed = get_deterministic_seed(username)
            if get_gender_from_seed(seed) == 'male':
                male_count += 1
            else:
                female_count += 1

    conn.commit()
    conn.close()
    print(f"  {db_name}: {updated} users updated ({male_count} male, {female_count} female)")
    return updated


def ensure_role_profiles():
    """Ensure all 'event' users have venue_profiles and all 'tents' users have tent_profiles."""
    print("\nEnsuring role profiles in probase.db...")
    conn = sqlite3.connect(probase_db)
    cursor = conn.cursor()

    # Ensure 'event' users have venue_profiles
    cursor.execute('''
        SELECT u.id, u.username FROM users u
        WHERE u.role = 'event'
        AND u.id NOT IN (SELECT user_id FROM venue_profiles)
    ''')
    event_users = cursor.fetchall()
    for user_id, username in event_users:
        cursor.execute('''
            INSERT INTO venue_profiles (user_id, capacity, daily_rate)
            VALUES (?, 100, 10000.0)
        ''', (user_id,))
    print(f"  Added {len(event_users)} venue_profiles for 'event' role users")

    # Ensure 'tents' users have tent_profiles
    cursor.execute('''
        SELECT u.id, u.username FROM users u
        WHERE u.role = 'tents'
        AND u.id NOT IN (SELECT user_id FROM tent_profiles)
    ''')
    tents_users = cursor.fetchall()
    for user_id, username in tents_users:
        cursor.execute('''
            INSERT INTO tent_profiles (user_id, tent_types, daily_rate)
            VALUES (?, 'Marquee, Gazebo, Dome', 8000.0)
        ''', (user_id,))
    print(f"  Added {len(tents_users)} tent_profiles for 'tents' role users")

    conn.commit()
    conn.close()


def main():
    print("=" * 60)
    print("ADDING PROFILE IMAGES AND FIXING ROLE PROFILES")
    print("=" * 60)
    print()

    # Add profile images to all databases
    add_profile_images_to_db(curyent_db, 'curyent.db')
    add_profile_images_to_db(booking_db, 'booking.db')
    add_profile_images_to_db(probase_db, 'probase.db')
    add_profile_images_to_db(social_db, 'social.db')

    # Ensure role profiles exist
    ensure_role_profiles()

    print()
    print("=" * 60)
    print("PROFILE IMAGES ADDED SUCCESSFULLY!")
    print("=" * 60)
    print()
    print("All users now have unique avatar images.")
    print("'event' role users have venue_profiles entries.")
    print("'tents' role users have tent_profiles entries.")
    print()
    print("Reload your web app to see the changes.")
    print("=" * 60)


if __name__ == '__main__':
    main()
