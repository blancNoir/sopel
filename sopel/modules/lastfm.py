"""
lastfm.py - last.fm checker for willie bot
Modified by Meicceli

Original can be found here https://github.com/mulcare/willie-modules
Licensing: https://github.com/mulcare/willie-modules/blob/master/LICENSE
"""
from sopel import web
from sopel.module import commands, example
from bs4 import BeautifulSoup
import json
import sys
import urllib

#Postaa taa luvux 1 jos haluut tulostaa api urlin
postapiurl = 0

#randomin apikey = 1d234424fd93e18d503758bf2714859e
#mun apikey      = 782c02b1c96ae181d83850f050509103

@commands('fm', 'np', 'last', 'lastfm')
def lastfm(willie, trigger):
    user = ''
    if trigger.nick == 'TheShinyPanda':
      return
    if trigger.group(2):
        user = trigger.group(2).replace("@", trigger.nick)
    if not (user and user != ''):
        user = willie.db.get_nick_value(trigger.nick, 'lastfm_user')
        if not user:
            willie.reply("Invalid username given or no username set. Use .fmset to set a username.")
            return
    #username variable prepared for insertion into REST string
    user = user.lower()
    quoted_user = web.quote(user)
    #json formatted output for recent track
    try:
        recent_page = web.get("http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=%s&api_key=782c02b1c96ae181d83850f050509103&format=json" % (quoted_user))
    except Exception, e:
        willie.say("last.fm is currently having technical difficulties. See .fmstatus for more information.")
        return

    try:
        recent_track = json.loads(recent_page)['recenttracks']['track'][0]
    except KeyError:
        willie.say("Couldn't find user")
        sys.exit(0)
    #artist and track name pulled from recent_track
    quoted_artist = web.quote(recent_track['artist']['#text'])
    quoted_track = web.quote(recent_track['name'])
    #json formatted track info
    trackinfo_page = urllib.urlopen("http://ws.audioscrobbler.com/2.0/?method=track.getInfo&artist=%s&track=%s&username=%s&api_key=782c02b1c96ae181d83850f050509103&format=json" % (quoted_artist, quoted_track, quoted_user))
    #track playcount and loved stats
    loved = 0
    try:
      trackinfo = json.loads(trackinfo_page.read())['track']
      playcount = trackinfo['userplaycount']
      loved = int(trackinfo['userloved'])
    except KeyError:
        playcount = "unknown"
    album = '(' + recent_track['album']['#text'] + ') '
    if len(recent_track['album']['#text']) == 0:
        album = ''

    try:
        if loved > 0:
            willie.say('\x035' + u'\u2665' +'\x03 %s is playing %s - %s %s(%s plays)' % (trigger.nick, recent_track['artist']['#text'], recent_track['name'], album, playcount))
        else:
            willie.say('%s is playing %s - %s %s(%s plays)' % (trigger.nick, recent_track['artist']['#text'], recent_track['name'], album, playcount))
    except KeyError:
        willie.say("Couldn't find any recent tracks")

@commands('fmset')
@example('.fmset daftpunk69')
def update_lastfm_user(bot, trigger):
    if not trigger.group(2):
        bot.reply("Please provide your lastfm username after .fmset")
        return
    user = trigger.group(2)
    bot.db.set_nick_value(trigger.nick, 'lastfm_user', user)
    bot.reply('Thanks, ' + user)


lastfm.rate = 0
lastfm.priority = 'low'
