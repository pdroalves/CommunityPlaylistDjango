from django.contrib import admin
from models import Channel,Playlist,Vote

# Actions

def set_played(modeladmin,request,queryset):
	queryset.update(played=True)
def set_not_played(modeladmin,request,queryset):
	queryset.update(played=False)
def set_removed(modeladmin,request,queryset):
	queryset.update(removed=True)
def set_not_removed(modeladmin,request,queryset):
	queryset.update(removed=False)

# Register your models here.
class VoteInLine(admin.TabularInline):
	model = Vote
	extra = 1

class PlaylistAdmin(admin.ModelAdmin):
	list_display = ('id','channel','title','duration','url','played','removed')
	list_filter = ['channel','played','removed']
	inlines = [VoteInLine]
	actions = [set_played,set_not_played,set_removed,set_not_removed]


set_played.short_description = "Set played"
set_not_played.short_description = "Set not played"
set_removed.short_description = "Set removed"
set_not_removed.short_description = "Set not removed"

admin.site.register(Channel)
admin.site.register(Playlist,PlaylistAdmin)
