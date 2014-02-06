from django.contrib import admin
from models import Channel,Playlist,Vote

# Register your models here.
class VoteInLine(admin.TabularInline):
	model = Vote
	extra = 1

class PlaylistAdmin(admin.ModelAdmin):
	list_display = ('channel','url','played','removed')
	list_filter = ['channel','played','removed']
	inlines = [VoteInLine]

admin.site.register(Channel)
admin.site.register(Playlist,PlaylistAdmin)
