"""
Group Management System
Advisor-client groups, discussion groups, course groups
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import uuid

class GroupType(Enum):
    ADVISOR_CLIENT = "advisor_client"      # 1-on-1 advisor relationship
    COURSE = "course"                       # Learning group
    DISCUSSION = "discussion"             # Open discussion
    PRIVATE = "private"                     # Closed group
    SIGNALS = "signals"                     # Trading signals group

class MemberRole(Enum):
    ADMIN = "admin"
    MODERATOR = "moderator"
    MEMBER = "member"
    VIEWER = "viewer"

@dataclass
class GroupMember:
    user_id: str
    role: MemberRole
    joined_at: datetime
    last_active: datetime

@dataclass
class Group:
    id: str
    name: str
    description: str
    group_type: GroupType
    creator_id: str
    members: Dict[str, GroupMember]
    is_private: bool
    created_at: datetime

class GroupManager:
    """
    Manage groups for advisor-client relationships and communities
    """
    
    def __init__(self):
        self.groups: Dict[str, Group] = {}
        self.user_groups: Dict[str, List[str]] = {}  # user_id -> group_ids
    
    def create_group(self,
                    name: str,
                    description: str,
                    group_type: GroupType,
                    creator_id: str,
                    is_private: bool = False) -> Group:
        """Create a new group"""
        
        group = Group(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            group_type=group_type,
            creator_id=creator_id,
            members={},
            is_private=is_private,
            created_at=datetime.now()
        )
        
        # Add creator as admin
        group.members[creator_id] = GroupMember(
            user_id=creator_id,
            role=MemberRole.ADMIN,
            joined_at=datetime.now(),
            last_active=datetime.now()
        )
        
        self.groups[group.id] = group
        
        # Track in user's groups
        if creator_id not in self.user_groups:
            self.user_groups[creator_id] = []
        self.user_groups[creator_id].append(group.id)
        
        return group
    
    def join_group(self, group_id: str, user_id: str, 
                   role: MemberRole = MemberRole.MEMBER) -> bool:
        """Add member to group"""
        if group_id not in self.groups:
            return False
        
        group = self.groups[group_id]
        
        # Check if private and user not invited
        if group.is_private and user_id not in group.members:
            return False
        
        if user_id in group.members:
            return False  # Already a member
        
        group.members[user_id] = GroupMember(
            user_id=user_id,
            role=role,
            joined_at=datetime.now(),
            last_active=datetime.now()
        )
        
        # Track in user's groups
        if user_id not in self.user_groups:
            self.user_groups[user_id] = []
        self.user_groups[user_id].append(group_id)
        
        return True
    
    def leave_group(self, group_id: str, user_id: str) -> bool:
        """Remove member from group"""
        if group_id not in self.groups:
            return False
        
        group = self.groups[group_id]
        
        if user_id in group.members:
            del group.members[user_id]
            
            # Remove from user's groups
            if user_id in self.user_groups and group_id in self.user_groups[user_id]:
                self.user_groups[user_id].remove(group_id)
            
            return True
        return False
    
    def update_member_role(self, group_id: str, admin_id: str, 
                          target_user_id: str, new_role: MemberRole) -> bool:
        """Update member role (admin only)"""
        if group_id not in self.groups:
            return False
        
        group = self.groups[group_id]
        
        # Check if admin has permission
        if admin_id not in group.members:
            return False
        if group.members[admin_id].role not in [MemberRole.ADMIN, MemberRole.MODERATOR]:
            return False
        
        if target_user_id in group.members:
            group.members[target_user_id].role = new_role
            return True
        return False
    
    def get_group(self, group_id: str) -> Optional[Group]:
        """Get group by ID"""
        return self.groups.get(group_id)
    
    def get_user_groups(self, user_id: str, group_type: Optional[GroupType] = None) -> List[Group]:
        """Get all groups a user is in"""
        group_ids = self.user_groups.get(user_id, [])
        groups = [self.groups[gid] for gid in group_ids if gid in self.groups]
        
        if group_type:
            groups = [g for g in groups if g.group_type == group_type]
        
        return groups
    
    def get_group_members(self, group_id: str) -> List[Dict]:
        """Get all members of a group"""
        if group_id not in self.groups:
            return []
        
        members = []
        for user_id, member in self.groups[group_id].members.items():
            members.append({
                'user_id': user_id,
                'role': member.role.value,
                'joined_at': member.joined_at.isoformat(),
                'last_active': member.last_active.isoformat()
            })
        return members
    
    def update_last_active(self, group_id: str, user_id: str):
        """Update last active timestamp"""
        if group_id in self.groups and user_id in self.groups[group_id].members:
            self.groups[group_id].members[user_id].last_active = datetime.now()
    
    # Specific group types
    def create_advisor_client_group(self, advisor_id: str, client_id: str) -> Group:
        """Create a 1-on-1 advisor-client group"""
        group = self.create_group(
            name=f"Advisor Session: {client_id}",
            description="Private financial advisory session",
            group_type=GroupType.ADVISOR_CLIENT,
            creator_id=advisor_id,
            is_private=True
        )
        
        # Add client as member
        self.join_group(group.id, client_id, MemberRole.MEMBER)
        
        return group
    
    def create_signals_group(self, creator_id: str, name: str) -> Group:
        """Create a trading signals group"""
        return self.create_group(
            name=name,
            description="Premium trading signals and alerts",
            group_type=GroupType.SIGNALS,
            creator_id=creator_id,
            is_private=True
        )
