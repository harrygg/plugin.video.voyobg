# -*- coding: utf-8 -*-
import re
import sys
import xbmc
import xbmcgui
import xbmcplugin
from resources.lib.actions import *

reload(sys)  
sys.setdefaultencoding('utf8')

if not settings.configured:
  settings.open()
  settings.configured = True
  
if not settings.device_id or settings.device_id == "":
  settings.device_id = get_unique_device_id()

def show_sections():
  if not userLogin():
    xbmc.executebuiltin('Notification(%s,%s,5000,%s)' % ("Грешка", 'Неуспшно вписване', 'DefaultFolder.png'))
    return
  
  if not deviceIsRegistered():
    errors = deviceRegister()
    if errors:
      dialog = xbmcgui.Dialog()
      res = dialog.yesno("Грешка", errors)
      if res:
        devices = deviceGet()
        i = dialog.select("Избери устройство за изтриване:", devices["names"])
        if deviceRemove(devices["ids"][i]):
          errors = deviceRegister()
          if errors:
            notify_error(errors)
        else:
          notify_error("Грешка при изтриване на устройство. Опитайте ръчно през сайта.")
          return
      else:
        return
  
  id = 1
  batch = JsonBatch()
  rpc = JsonRpc(id)
  params = {"session": settings.session, "chargingType": "SP" }
  batch.append( rpc.sections(params) )
  batch.execute()
  items = batch.get_result_by_id(id)['list']
  
  for item in items:
    url = make_url({"action":"show_section", "sectionId": item["sectionId"]})
    name = '%s (%s)' % (item['title'], item.get('numOfProducts'))
    li = xbmcgui.ListItem(name)
    xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, li, True)

  update('browse', 'Categories')

def show_section(sectionId):
  products = sectionProducts(sectionId)  
  for product in products:
    url = make_url({"action":"show_product", "productId":product["productId"], "mediaId":product["mediaId"]})
    li = xbmcgui.ListItem(product["title"], iconImage=product["logo"], thumbnailImage=product["logo"])
    xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, li, True)
   
    
def show_product(mediaId, productId):
  headers = "User-agent: stagefright/1.2 (Linux;Android 6.0)"
  product = getProductUrl(mediaId, productId)
  if not product["isAllowed"]:
    dialog = xbmcgui.Dialog()
    dialog = dialog.ok("Грешка", product["errors"])
    return
  url = product["url"]
  
  li = xbmcgui.ListItem("Play")
  li.setInfo( type = "Video", infoLabels = { "Title" : "Play", "Plot": ""} )
  if settings.use_isa:
    li.setProperty('inputstreamaddon', 'inputstream.adaptive')
    li.setProperty('inputstream.adaptive.manifest_type', 'hls')
    li.setProperty('inputstream.adaptive.stream_headers', headers)
  url += "|" + headers
  li.setProperty("IsPlayable", str(True))
  xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, li)

params = get_params()
action = params.get("action")
mediaId = params.get("mediaId")
productId = params.get("productId")
sectionId = params.get("sectionId")

if not action:
	show_sections()
elif action == 'show_section':
	show_section(sectionId)
elif action == 'show_product':
	show_product(mediaId, productId)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
