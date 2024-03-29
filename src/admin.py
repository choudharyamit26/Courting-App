from django.contrib import admin
from .models import (UserDetail, UserInstagramPic, RegisterUser,
                     MatchedUser, RequestMeeting, ScheduleMeeting,
                     Feedback, ContactUs, AboutUs, SubscriptionPlans, DeactivateAccount, BlockedUsers,PopNotification)

admin.site.register(UserDetail)
admin.site.register(RegisterUser)
admin.site.register(UserInstagramPic)
admin.site.register(MatchedUser)
admin.site.register(RequestMeeting)
admin.site.register(ScheduleMeeting)
admin.site.register(Feedback)
admin.site.register(ContactUs)
admin.site.register(AboutUs)
admin.site.register(SubscriptionPlans)
admin.site.register(DeactivateAccount)
admin.site.register(BlockedUsers)
admin.site.register(PopNotification)
