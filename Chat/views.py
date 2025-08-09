from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.templatetags.static import static
from .models import *

@login_required
def ChatView(request, room_id=None):

    user = request.user
    profile = getattr(user, 'profile', None)
    if not profile:
        return redirect('profile_setup')

    rooms = ChatRoom.objects.filter(members=profile).prefetch_related('members__user')


    chat_list_data = []
    for room in rooms:
        last_msg = room.messages.order_by("-timestamp").first()

        other = room.members.exclude(id=profile.id).first()

        other_profile = other if other else profile
        display_name = display_name_for(other_profile)
        picture = picture_url_for(other_profile)

        chat_list_data.append({
            "id": room.id,
            "name": display_name,
            "last_message": last_msg.content if last_msg else "",
            "time": last_msg.timestamp.strftime("%H:%M") if last_msg else "",
            "unread": 0,
            "picture": picture,
        })
    
    if room_id:
        chat = get_object_or_404(rooms, id=room_id)
    else :
        chat = False
        
    if chat:
        messages_qs = chat.messages.select_related('user__user').order_by('timestamp')
    else:
        messages_qs = []


    message_data = []
    for msg in messages_qs:
        message_data.append({
            "text": msg.content,
            "sent": (msg.user == profile),   # msg.user হওয়া উচিত profile (model অনুসারে)
            "time": msg.timestamp.strftime("%H:%M"),
        })

    current_chat_name = "No Chat Selected"
    if chat:
        found = next((c for c in chat_list_data if c['id'] == chat.id), None)
        current_chat_name = found['name'] if found else display_name_for(profile)
        other_profile = chat.members.exclude(id=profile.id).first() or profile
        picture = picture_url_for(other_profile)

    
    if room_id is None:
        context = {
        "chats": chat_list_data,
        'nochat':True,
        "user_profile": profile,
    }
        return render(request, "chat.html" ,context)
    else:
        context = {
        "chats": chat_list_data,
        "current_chat": {
            "id": chat.id if chat else None,
            "name": current_chat_name,
            "messages": message_data,
            'picture':picture
        },
        "room_id": room_id,
        "user_profile": profile,
    }
        return render(request, "chat.html", context)


# def SearchView(request):
#     user = request.user
#     profile = request.user.profile

#     if request.method == "POST":
#         query = request.POST.get("name", "").strip()
#         print('search_term----', query)

#         rooms = ChatRoom.objects.filter(members=profile).prefetch_related('members__user')

#         chat_list_data = []
#         for room in rooms:
#             last_msg = room.messages.order_by("-timestamp").first()
            
#             # Get matching members (case-insensitive)
#             other_members = room.members.exclude(id=profile.id).filter(
#                 Q(Name__icontains=query) | 
#                 Q(user__username__icontains=query)
#             )
            
#             # If searching and no matches, skip this room
#             if query and not other_members.exists():
#                 continue
                
#             # Get first matching member, or first member if no query
#             other = other_members.first() if query else room.members.exclude(id=profile.id).first()
#             other_profile = other if other else profile

#             chat_list_data.append({
#                 "id": room.id,
#                 "name": display_name_for(other_profile),
#                 "last_message": last_msg.content if last_msg else "",
#                 "time": last_msg.timestamp.strftime("%H:%M") if last_msg else "",
#                 "unread": 0,
#                 "picture": picture_url_for(other_profile),
#             })

#         context = {
#             "query": query,
#             "chats": chat_list_data,
#             "nochat": True,  # Only True if no results
#             "user_profile": profile,
#             "search_mode": bool(query),  # Tell template we're searching
#         }
#         return render(request, "chat.html", context)
        
#     return redirect('/chat/')




def SearchView(request):
    user = request.user
    profile = request.user.profile

    if request.method == "POST":
        query = request.POST.get("name", "").strip()

        # ১. বর্তমান ইউজারের সব চ্যাট রুম খুঁজে বের করুন
        existing_rooms = ChatRoom.objects.filter(members=profile).prefetch_related('members__user')
        
        # ২. সার্চ কুয়েরি অনুযায়ী সকল প্রোফাইল খুঁজুন (নাম বা ইউজারনেমে)
        all_matching_profiles = Profile.objects.filter(
            Q(name__icontains=query) | 
            Q(user__username__icontains=query)
        ).exclude(id=profile.id)  # নিজের প্রোফাইল বাদ দিন

        chat_list_data = []
        
        for profile in all_matching_profiles:
            # ৩. চেক করুন ইতিমধ্যে চ্যাট রুম আছে কিনা
            room = existing_rooms.filter(members=profile).first()
            
            if room:
                # ৪. যদি রুম থাকে, লাস্ট মেসেজ সহ ডিটেইলস যোগ করুন
                last_msg = room.messages.order_by("-timestamp").first()
                chat_list_data.append({
                    "id": room.id,
                    "name": display_name_for(profile),
                    "last_message": last_msg.content if last_msg else "",
                    "time": last_msg.timestamp.strftime("%H:%M") if last_msg else "",
                    "unread": 0,
                    "picture": picture_url_for(profile),
                    "has_room": True  # ফ্রন্টএন্ডকে জানাবে রুম আছে
                })
            else:
                # ৫. যদি রুম না থাকে, শুধু প্রোফাইল ইনফো দিন
                chat_list_data.append({
                    "id": profile.user.id,  # ইউজার আইডি ব্যবহার করুন
                    "name": display_name_for(profile),
                    "last_message": "",
                    "time": "",
                    "unread": 0,
                    "picture": picture_url_for(profile),
                    "has_room": False  # ফ্রন্টএন্ডকে জানাবে রুম নেই
                })
        print('chat_list_data,',chat_list_data)
        context = {
            "query": query,
            "chats": chat_list_data,
            "nochat": True,
            "user_profile": profile,
            "search_mode": True,

        }
        # print(context)
        return render(request, "chat.html", context)
        
    return redirect('/chat/')

def create_chat_room(request, user_id):
    # ৬. নতুন চ্যাট রুম ক্রিয়েট করার ভিউ
    current_user = request.user
    other_user = get_object_or_404(User, id=user_id)
    
    # চেক করুন রুম ইতিমধ্যে আছে কিনা
    existing_room = ChatRoom.objects.filter(
        members=current_user.profile
    ).filter(
        members=other_user.profile
    ).first()
    
    if existing_room:
        return redirect('chat-room' \
        '', room_id=existing_room.id)
    
    # নতুন রুম তৈরি করুন
    new_room = ChatRoom.objects.create()
    new_room.members.add(current_user.profile, other_user.profile)
    new_room.save()
    
    return redirect('chat-room', room_id=new_room.id)



def display_name_for(p):
    if not p:
        return ""
    name = getattr(p, 'name', None) or getattr(p, 'name', None)
    if name:
        return name
    full = getattr(p.user, 'get_full_name', lambda: "")()
    return full or getattr(p.user, 'username', "")

def picture_url_for(p):
        default_avatar = static('images/default-avatar.jpg')
        if not p:
            print('No profile provided')
            return default_avatar
        try:
            image_field = getattr(p, 'image', None)
            if image_field and hasattr(image_field, 'url'):
                print(f'Using image URL: {image_field.url}')
                return image_field.url
            else:
                print('Profile has no image or image url attribute')
        except Exception as e:
            print(f'Exception while accessing image url: {e}')
        return default_avatar