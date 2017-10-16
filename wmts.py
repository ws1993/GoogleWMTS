#coding=utf-8
'''
Created on 2012-7-19
将google Map转化为WMST服务
@author: fiftyk
'''
import tornado.ioloop
import tornado.web
import sqlite3,StringIO,math
from tornado.web import GZipContentEncoding

class WMTSHandler(tornado.web.RequestHandler):
    TileMatrix = '''<TileMatrix>
                <ows:Identifier>%s</ows:Identifier>
                <ScaleDenominator>%s</ScaleDenominator>
                <TopLeftCorner>-20037508.342787 20037508.342787</TopLeftCorner>
                <TileWidth>256</TileWidth>
                <TileHeight>256</TileHeight>
                <MatrixWidth>%s</MatrixWidth>
                <MatrixHeight>%s</MatrixHeight>
            </TileMatrix>'''
    
    url_pattern = {
        "street":"http://mt0.google.cn/vt/lyrs=m@169000000&hl=zh-CN&gl=cn&x=%s&y=%s&z=%s&s=",
        "satellite":"http://khm1.google.com/kh/v=114&src=app&x=%s&y=%s&z=%s",
        "local": "http://127.0.0.1:9001/TMS/%s/%s/%s"
    }
    
    def initialize(self):
        pass

    def get(self):
        #?SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetCapabilities
        #TileRow=1&TileCol=0
        row = self.get_argument("TileRow",-1)
        col = self.get_argument("TileCol",-1)
        level = self.get_argument("TileMatrix",-1)
        layer = self.get_argument("layer","street")
        
        if row != -1 and col != -1 and level != -1:
            url = self.url_pattern.get(layer)%(col,row,level.replace("EPSG:3785:",""))
            #print url
            self.redirect(url)
        else:
            self.set_header("Content-Type", "text/xml;charset=utf-8")
            TileMatrix_List = ""
        
            for i in range(20):
                level = str(i)
                scale = str(559082264.0287178 /math.pow(2,i))
                width = str(1 << i)
                TileMatrix_List += self.TileMatrix%(level,scale,width,width)
            
            self.xml = open("wmts.xml").read()%TileMatrix_List
            self.write(self.xml)

    post = get

GZipContentEncoding.CONTENT_TYPES.add("image/png")

application = tornado.web.Application([
    (r"/wmts",WMTSHandler)
],"",None,gzip=True)

application.listen(5555)
tornado.ioloop.IOLoop.instance().start()