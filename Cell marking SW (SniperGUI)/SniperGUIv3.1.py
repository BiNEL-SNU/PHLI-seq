#-------------------------------------------------------------------------------
# Author:      Amos Chungwon Lee, Seoul National University, Seoul, Korea
#
# Created:     02-01-2015
#-------------------------------------------------------------------------------

import wx
import os
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL import TiffImagePlugin
import sys
import time
import ctypes

class MyGUIApp(wx.App,wx.Frame):

    def __init__(self, redirect=False, filename=None):

        ##sys.stderr.write('%s'%(Image.__version__))


        wx.App.__init__(self, redirect, filename)
        self.frame = wx.Frame(None, title='SniperGUIv3.0')
        self.panel = wx.Panel(self.frame)

        self.filename  = ''
        self.dirname = ''
        width, height = wx.DisplaySize()
        user32 = ctypes.windll.user32
        ResW = user32.GetSystemMetrics(0)
        ResH = user32.GetSystemMetrics(1)
        if ResW >= ResH:
            self.pictureMaxSize = ResH-200
        else:
            self.pictureMaxSize = ResW
        self.M=1
        self.renewPixel=3

        img = wx.EmptyImage(self.pictureMaxSize, self.pictureMaxSize)
        self.imageCtrl = wx.StaticBitmap(self.panel, wx.ID_ANY, wx.BitmapFromImage(img))

        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.mainSizer.Add(self.imageCtrl, 0, wx.ALL|wx.CENTER, 5)
        self.panel.SetSizer(self.mainSizer)
        self.mainSizer.Fit(self.frame)

        self.createMenus()
        self.connectItemsWithEvents()
        self.createKeyboardShortcuts()

        self.frame.SetMenuBar(self.menuBar)

        self.imageCtrl.Bind(wx.EVT_LEFT_DOWN,self.Mover1)
        self.imageCtrl.Bind(wx.EVT_MOTION,self.Mover2)
        self.imageCtrl.Bind(wx.EVT_LEFT_DCLICK,self.Enlarger)
        self.imageCtrl.Bind(wx.EVT_RIGHT_DCLICK,self.Shrinker)

        self.fontflag=False

        self.frame.Show()

    def connectItemsWithEvents(self) :
        self.Bind(wx.EVT_MENU, self.openEvent, self.openItem)
        self.Bind(wx.EVT_MENU, self.DataSave, self.saveItem)
        self.Bind(wx.EVT_MENU, self.open2, self.openItem2)
        self.Bind(wx.EVT_MENU, self.open3, self.openItem3)
        self.Bind(wx.EVT_MENU, self.open4, self.openItem4)


    def createKeyboardShortcuts(self) :
        self.accel_tbl = wx.AcceleratorTable([(wx.ACCEL_CTRL, ord('O'), self.openItem.GetId()),
                                            (wx.ACCEL_CTRL, ord('O'), self.saveItem.GetId()),
                                              (wx.ACCEL_CTRL, ord('O'), self.openItem2.GetId()),
                                              (wx.ACCEL_CTRL, ord('O'), self.openItem3.GetId()),
                                              (wx.ACCEL_CTRL, ord('O'), self.openItem4.GetId())])
        self.frame.SetAcceleratorTable(self.accel_tbl)

    def createMenus(self) :
        self.menuBar = wx.MenuBar()
        self.menuFile = wx.Menu()

        self.menuBar.Append(self.menuFile, '&File')
        self.openItem = wx.MenuItem(self.menuFile, wx.NewId(), u'&open ...\tCTRL+O')
        self.openItem2 = wx.MenuItem(self.menuFile, wx.NewId(), u'&open 2nd image ...\tCTRL+2')
        self.openItem3 = wx.MenuItem(self.menuFile, wx.NewId(), u'&open 3rd image ...\tCTRL+3')
        self.openItem4 = wx.MenuItem(self.menuFile, wx.NewId(), u'&open 4th image ...\tCTRL+4')

        self.saveItem = wx.MenuItem(self.menuFile, wx.NewId(), u'&save ...\tCTRL+S')

        #self.openItem.SetBitmap(wx.Bitmap('images/document-open.tif'))
        self.menuFile.AppendItem(self.openItem)
        self.menuFile.AppendItem(self.openItem2)
        self.menuFile.AppendItem(self.openItem3)
        self.menuFile.AppendItem(self.openItem4)
        self.menuFile.AppendItem(self.saveItem)



    def DataSave(self,event):
        # TARGET DATA
        g=open(os.path.join(self.dirname,self.filename.split('.')[0]+'_output.txt'),'w')
        g.write('%s\t%s\t%s\t%s\t%s\t%s\n'%('INDEX','X1','Y1','X2','Y2','NOTE'))
        for enum, data in enumerate(self.L):
            if self.L[enum][0] == None:continue
            g.write('%d\t%d\t%d\t%d\t%d\t%s\n'%(enum+1,self.L[enum][0],self.L[enum][1],self.L[enum][2],self.L[enum][3],self.L[enum][4]))
        g.close()

        # TARGET IMAGE
        self.im.save(os.path.join(self.dirname, self.filename.split('.')[0]+'_target.tif'))


    def Quit(self):
        del self.im
        os.remove(os.path.join(self.dirname,'copy.tif'))
        os.remove(os.path.join(self.dirname,'temp.tif'))



    def openEvent(self, event) :
        openDialog = wx.FileDialog(self.frame, u'Open file', "File", "", "*.*", wx.OPEN)
        if openDialog.ShowModal() == wx.ID_OK :
            self.filename = openDialog.GetFilename()
            self.dirname = openDialog.GetDirectory()

            self.original=Image.open(os.path.join(self.dirname, self.filename))
            self.original.save(os.path.join(self.dirname, 'copy.tif'))
            self.im=Image.open(os.path.join(self.dirname, 'copy.tif'))
            self.im1 = self.im
            self.W,self.H=self.im.size


            self.x1, self.y1=0, 0
            self.x2, self.y2=self.W, self.H

            if self.W>self.H: self.R=self.pictureMaxSize/float(self.W)
            else: self.R=self.pictureMaxSize/float(self.H)
            self.W0=int(self.W*self.R)
            self.H0=int(self.H*self.R)
            self.im.resize((self.W0,self.H0)).save(self.dirname+"/temp.tif")

            self.button1=wx.Button(self.panel,label="Select", pos = (300,self.H0+30),size = (60,20))
            self.button2=wx.Button(self.panel,label="Select", pos = (300,self.H0+50),size = (60,20))
            self.button3=wx.Button(self.panel,label="Select", pos = (300,self.H0+70),size = (60,20))
            self.Bind(wx.EVT_BUTTON, self.AreaSelection1, self.button1)
            self.Bind(wx.EVT_BUTTON, self.AreaSelection2, self.button2)
            self.Bind(wx.EVT_BUTTON, self.AreaSelection3, self.button3)


            self.buttonCancel1=wx.Button(self.panel,label="Cancel", pos = (360,self.H0+30),size = (60,20))
            self.buttonCancel2=wx.Button(self.panel,label="Cancel", pos = (360,self.H0+50),size = (60,20))
            self.buttonCancel3=wx.Button(self.panel,label="Cancel", pos = (360,self.H0+70),size = (60,20))
            self.Bind(wx.EVT_BUTTON, self.clearData1, self.buttonCancel1)
            self.Bind(wx.EVT_BUTTON, self.clearData2, self.buttonCancel2)
            self.Bind(wx.EVT_BUTTON, self.clearData3, self.buttonCancel3)

            self.index = 1
            self.L = [ [None]*5 for i in range(1000) ]

            self.ListBefore1=wx.Button(self.panel,label=u"\u25C0", pos =(360,self.H0+10),size = (20,20))

            self.ListAfter1=wx.Button(self.panel,label=u"\u25B6", pos =(380,self.H0+10),size = (20,20))
            self.Bind(wx.EVT_BUTTON, self.ListBefore, self.ListBefore1)
            self.Bind(wx.EVT_BUTTON, self.ListAfter, self.ListAfter1)

            self.NoteStatic = wx.StaticText(self.panel, -1, "Description", pos = (20,self.H0+10))

            self.Note1 = wx.TextCtrl(self.panel, pos = (20,self.H0+30), size=(190,20))
            self.Note2 = wx.TextCtrl(self.panel, pos = (20,self.H0+50), size=(190,20))
            self.Note3 = wx.TextCtrl(self.panel, pos = (20,self.H0+70), size=(190,20))

            self.Number1 = wx.StaticText(self.panel, -1, "1", pos = (5,self.H0+30))
            self.Number2 = wx.StaticText(self.panel, -1, "2", pos = (5,self.H0+50))
            self.Number3 = wx.StaticText(self.panel, -1, "3", pos = (5,self.H0+70))

            self.CoordinateNote1 = wx.TextCtrl(self.panel, pos = (450,self.H0+30), size = (190,20))
            self.CoordinateNote2 = wx.TextCtrl(self.panel, pos = (450,self.H0+50), size = (190,20))

            self.GetCoordinateButton = wx.Button(self.panel,label = "Get Pictures!", pos = (670,self.H0+30), size = (150,20))
            self.Bind(wx.EVT_BUTTON, self.GetPixel, self.GetCoordinateButton)
            
            self.draw(os.path.join(self.dirname,"temp.tif"))
            self.frame.SetSize((800,self.H0+200))

        openDialog.Destroy()
        time.sleep(1)

    def open2(self, event):
        openDialog = wx.FileDialog(self.frame, u'Open file', "File", "", "*.*", wx.OPEN)
        if openDialog.ShowModal() == wx.ID_OK :
            self.filename = openDialog.GetFilename()
            self.dirname = openDialog.GetDirectory()
            self.im2=Image.open(os.path.join(self.dirname, self.filename))

    def open3(self, event):
        openDialog = wx.FileDialog(self.frame, u'Open file', "File", "", "*.*", wx.OPEN)
        if openDialog.ShowModal() == wx.ID_OK :
            self.filename = openDialog.GetFilename()
            self.dirname = openDialog.GetDirectory()
            self.im3=Image.open(os.path.join(self.dirname, self.filename))

    def open4(self, event):
        openDialog = wx.FileDialog(self.frame, u'Open file', "File", "", "*.*", wx.OPEN)
        if openDialog.ShowModal() == wx.ID_OK :
            self.filename = openDialog.GetFilename()
            self.dirname = openDialog.GetDirectory()
            self.im4=Image.open(os.path.join(self.dirname, self.filename))
        
    
    def draw(self, filename) :
        image_name = filename
        img = wx.Image(filename, wx.BITMAP_TYPE_ANY)
        W = img.GetWidth()
        H = img.GetHeight()
        if W > H:
            NewW = self.pictureMaxSize
            NewH = self.pictureMaxSize * H / W
        else:
            NewH = self.pictureMaxSize
            NewW = self.pictureMaxSize * W / H
        img = img.Scale(NewW,NewH)
        self.imageCtrl.SetBitmap(wx.BitmapFromImage(img))
        self.panel.Refresh()

    def Mover1(self,evt):
        self.x_before, self.y_before = evt.GetX(), evt.GetY()

    def Mover2(self,evt):
        if evt.LeftIsDown() and evt.ShiftDown():
            self.x_after, self.y_after = evt.GetX(), evt.GetY()
            if self.Distance((self.x_before,self.y_before), (self.x_after, self.y_after))> self.renewPixel:

                os.remove(os.path.join(self.dirname,"temp.tif"))
                im_base=self.im.crop((self.x1,self.y1, self.x2,self.y2)).resize((self.W0,self.H0))
                color_layer =Image.new('RGBA', (self.W0,self.H0),(0,0,255))
                alpha_mask= Image.new('L',(self.W0,self.H0),0)
                alpha_mask_draw = ImageDraw.Draw(alpha_mask)
                alpha_mask_draw.rectangle([self.x_before,self.y_before,self.x_after,self.y_after],fill=50)
                Image.composite(color_layer, im_base, alpha_mask).save(self.dirname+"/temp.tif")
                self.draw(os.path.join(self.dirname,"temp.tif"))

                self.target_x1, self.target_y1=self.Convert(self.x_before, self.y_before)
                self.target_x2, self.target_y2=self.Convert(self.x_after, self.y_after)
            return 0

        if evt.LeftIsDown():
            self.x_after, self.y_after = evt.GetX(), evt.GetY()
            if self.Distance((self.x_before,self.y_before), (self.x_after, self.y_after))> self.renewPixel:
                os.remove(os.path.join(self.dirname,"temp.tif"))
                drag_x= int((self.x_after-self.x_before)/(self.R*self.M))
                drag_y= int((self.y_after-self.y_before)/(self.R*self.M))
                self.x1, self.y1= (self.x1-drag_x ,self.y1-drag_y)
                self.x2, self.y2= (self.x2-drag_x ,self.y2-drag_y)
                self.x_before=self.x_after
                self.y_before=self.y_after
                self.im.crop((self.x1,self.y1, self.x2,self.y2)).resize((self.W0,self.H0)).save(self.dirname+"/temp.tif")
                self.draw(os.path.join(self.dirname,"temp.tif"))



    def Enlarger(self,evt):
        if evt.ControlDown():
            X,Y=evt.GetX(), evt.GetY()
            X_converted, Y_converted = self.Convert(X,Y)

            self.M*=2

            os.remove(os.path.join(self.dirname,"temp.tif"))
            self.x1, self.y1= X_converted-self.W/(self.M*2),Y_converted-self.H/(self.M*2)
            self.x2, self.y2= X_converted+self.W/(self.M*2),Y_converted+self.H/(self.M*2)
            self.im.crop((self.x1,self.y1, self.x2,self.y2)).resize((self.W0,self.H0)).save(self.dirname+"/temp.tif")
            self.draw(os.path.join(self.dirname,"temp.tif"))


    def Shrinker(self, evt):
        if evt.ControlDown() and self.M>2:

            X,Y=evt.GetX(), evt.GetY()
            X_converted, Y_converted = self.Convert(X,Y)

            self.M/=2

            self.x1, self.y1= X_converted-self.W/(self.M*2),Y_converted-self.H/(self.M*2)
            self.x2, self.y2= X_converted+self.W/(self.M*2),Y_converted+self.H/(self.M*2)
            os.remove(os.path.join(self.dirname,"temp.tif"))
            self.im.crop((self.x1,self.y1, self.x2,self.y2)).resize((self.W0,self.H0)).save(self.dirname+"/temp.tif")
            self.draw(os.path.join(self.dirname,"temp.tif"))

        elif evt.ControlDown() and self.M==2:

            self.M-=1
            self.x1, self.y1 = 0,0
            self.x2, self.y2 = self.W, self.H

            os.remove(os.path.join(self.dirname,"temp.tif"))
            self.im.resize((self.W0,self.H0)).save(self.dirname+"/temp.tif")

            self.draw(os.path.join(self.dirname,"temp.tif"))


    def Convert(self,X,Y):
        X_conv=self.x1 + X/(self.R*self.M)
        Y_conv=self.y1 + Y/(self.R*self.M)
        return int(X_conv), int(Y_conv)

    def Distance(self,pos1,pos2):
        x1, y1= pos1[0], pos1[1]
        x2, y2= pos2[0], pos2[1]
        return pow((x1-x2)*(x1-x2)+(y1-y2)*(y1-y2),0.5)



    def clearData1(self,event):
        self.d = -1

        cropbox=(self.L[self.index+self.d][0]-5,self.L[self.index+self.d][1]-5,self.L[self.index+self.d][2]+5,self.L[self.index+self.d][3]+5)
        croped= self.original.crop(cropbox)
        self.im.paste(croped,box=cropbox)
        self.im.crop((self.x1,self.y1, self.x2,self.y2)).resize((self.W0,self.H0)).save(self.dirname+"/temp.tif")
        self.draw(os.path.join(self.dirname,"temp.tif"))

        self.L[self.index+self.d][0] = None
        self.L[self.index+self.d][1] = None
        self.L[self.index+self.d][2] = None
        self.L[self.index+self.d][3] = None
        self.L[self.index+self.d][4] = None
        self.Note1.SetValue('')
        self.saved1 = wx.StaticText(self.panel, -1, "            ", (220,self.H0+30))



    def clearData2(self,event):
        self.d = 0

        cropbox=(self.L[self.index+self.d][0]-5,self.L[self.index+self.d][1]-5,self.L[self.index+self.d][2]+5,self.L[self.index+self.d][3]+5)
        croped= self.original.crop(cropbox)
        self.im.paste(croped,box=cropbox)
        self.im.crop((self.x1,self.y1, self.x2,self.y2)).resize((self.W0,self.H0)).save(self.dirname+"/temp.tif")
        self.draw(os.path.join(self.dirname,"temp.tif"))

        self.L[self.index+self.d][0] = None
        self.L[self.index+self.d][1] = None
        self.L[self.index+self.d][2] = None
        self.L[self.index+self.d][3] = None
        self.L[self.index+self.d][4] = None
        self.Note2.SetValue('')
        self.saved2=wx.StaticText(self.panel, -1, "            ", pos=(220,self.H0+50))

    def clearData3(self,event):
        self.d = 1

        cropbox=(self.L[self.index+self.d][0]-5,self.L[self.index+self.d][1]-5,self.L[self.index+self.d][2]+5,self.L[self.index+self.d][3]+5)
        croped= self.original.crop(cropbox)
        self.im.paste(croped,box=cropbox)
        self.im.crop((self.x1,self.y1, self.x2,self.y2)).resize((self.W0,self.H0)).save(self.dirname+"/temp.tif")
        self.draw(os.path.join(self.dirname,"temp.tif"))

        self.L[self.index+self.d][0] = None
        self.L[self.index+self.d][1] = None
        self.L[self.index+self.d][2] = None
        self.L[self.index+self.d][3] = None
        self.L[self.index+self.d][4] = None
        self.Note3.SetValue('')
        self.saved3=wx.StaticText(self.panel, -1, "            ", pos=(220,self.H0+70))

    def AreaSelection1(self,event):
        self.d = -1
        self.L[self.index+self.d][0] = self.target_x1
        self.L[self.index+self.d][1] = self.target_y1
        self.L[self.index+self.d][2] = self.target_x2
        self.L[self.index+self.d][3] = self.target_y2
        self.NoteString = self.Note1.GetValue()
        self.L[self.index+self.d][4] = self.NoteString
        self.saved1 = wx.StaticText(self.panel, -1, "Saved!", (220,self.H0+30))

        self.CoordinateNote1.SetValue(str(self.target_x1) + " " + str(self.target_y1))
        self.CoordinateNote2.SetValue(str(self.target_x2) + " " + str(self.target_y2))
        ### save masked image ######################################################
        color_layer =Image.new('RGBA', (abs(self.target_x2-self.target_x1),abs(self.target_y2-self.target_y1)),(0,0,255))
        alpha_mask= Image.new('L',(abs(self.target_x2-self.target_x1),abs(self.target_y2-self.target_y1)),0)
        alpha_mask_draw = ImageDraw.Draw(alpha_mask)
        alpha_mask_draw.rectangle([0,0,self.target_x2-self.target_x1,self.target_y2-self.target_y1],fill=50)

        self.im_new2 = self.im.crop([self.target_x1,self.target_y1,self.target_x2,self.target_y2])
        ##self.im3 = self.im2.paste(alpha_mask, (0,0,self.target_x2-self.target_x1,self.target_y2-self.target_y1))

        self.imComp=Image.composite(color_layer,self.im_new2, alpha_mask)

        ## Print index on image
        self.FontSetting()
        draw=ImageDraw.Draw(self.imComp)
        draw.text((0,0), '%d'%(self.index), font=self.font)

        self.im.paste(self.imComp,[self.target_x1,self.target_y1,self.target_x2,self.target_y2])

        os.remove(os.path.join(self.dirname,"temp.tif"))
        self.im.crop([self.x1,self.y1, self.x2,self.y2]).resize((self.W0,self.H0)).save(self.dirname+"/temp.tif")
        self.draw(os.path.join(self.dirname,"temp.tif"))



    def AreaSelection2(self,event):
        self.d = 0
        self.L[self.index+self.d][0] = self.target_x1
        self.L[self.index+self.d][1] = self.target_y1
        self.L[self.index+self.d][2] = self.target_x2
        self.L[self.index+self.d][3] = self.target_y2
        self.NoteString = self.Note2.GetValue()
        self.L[self.index+self.d][4] = self.NoteString
        self.saved2=wx.StaticText(self.panel, -1, "Saved!", pos=(220,self.H0+50))

        self.CoordinateNote1.SetValue(str(self.target_x1) + " " + str(self.target_y1))
        self.CoordinateNote2.SetValue(str(self.target_x2) + " " + str(self.target_y2))
        ### save masked image ######################################################
        color_layer =Image.new('RGBA', (abs(self.target_x2-self.target_x1),abs(self.target_y2-self.target_y1)),(0,0,255))
        alpha_mask= Image.new('L',(abs(self.target_x2-self.target_x1),abs(self.target_y2-self.target_y1)),0)
        alpha_mask_draw = ImageDraw.Draw(alpha_mask)
        alpha_mask_draw.rectangle([0,0,self.target_x2-self.target_x1,self.target_y2-self.target_y1],fill=50)

        self.im_new2 = self.im.crop([self.target_x1,self.target_y1,self.target_x2,self.target_y2])
        ##self.im3 = self.im2.paste(alpha_mask, (0,0,self.target_x2-self.target_x1,self.target_y2-self.target_y1))

        self.imComp=Image.composite(color_layer,self.im_new2, alpha_mask)

        ## Print index on image
        self.FontSetting()
        draw=ImageDraw.Draw(self.imComp)
        draw.text((0,0), '%d'%(self.index+1), font=self.font)

        self.im.paste(self.imComp,[self.target_x1,self.target_y1,self.target_x2,self.target_y2])

        os.remove(os.path.join(self.dirname,"temp.tif"))
        self.im.crop([self.x1,self.y1, self.x2,self.y2]).resize((self.W0,self.H0)).save(self.dirname+"/temp.tif")
        self.draw(os.path.join(self.dirname,"temp.tif"))



    def AreaSelection3(self,event):
        self.d = 1
        self.L[self.index+self.d][0] = self.target_x1
        self.L[self.index+self.d][1] = self.target_y1
        self.L[self.index+self.d][2] = self.target_x2
        self.L[self.index+self.d][3] = self.target_y2
        self.NoteString = self.Note3.GetValue()
        self.L[self.index+self.d][4] = self.NoteString
        self.saved3=wx.StaticText(self.panel, -1, "Saved!", pos=(220,self.H0+70))

        self.CoordinateNote1.SetValue(str(self.target_x1) + " " + str(self.target_y1))
        self.CoordinateNote2.SetValue(str(self.target_x2) + " " + str(self.target_y2))
        ### save masked image ######################################################
        color_layer =Image.new('RGBA', (abs(self.target_x2-self.target_x1),abs(self.target_y2-self.target_y1)),(0,0,255))
        alpha_mask= Image.new('L',(abs(self.target_x2-self.target_x1),abs(self.target_y2-self.target_y1)),0)
        alpha_mask_draw = ImageDraw.Draw(alpha_mask)
        alpha_mask_draw.rectangle([0,0,self.target_x2-self.target_x1,self.target_y2-self.target_y1],fill=50)

        self.im_new2 = self.im.crop([self.target_x1,self.target_y1,self.target_x2,self.target_y2])
        ##self.im3 = self.im2.paste(alpha_mask, (0,0,self.target_x2-self.target_x1,self.target_y2-self.target_y1))

        self.imComp=Image.composite(color_layer,self.im_new2, alpha_mask)

        ## Print index on image
        self.FontSetting()
        draw=ImageDraw.Draw(self.imComp)
        draw.text((0,0), '%d'%(self.index+2), font=self.font)

        self.im.paste(self.imComp,[self.target_x1,self.target_y1,self.target_x2,self.target_y2])

        os.remove(os.path.join(self.dirname,"temp.tif"))
        self.im.crop([self.x1,self.y1, self.x2,self.y2]).resize((self.W0,self.H0)).save(self.dirname+"/temp.tif")
        self.draw(os.path.join(self.dirname,"temp.tif"))

    def GetPixel(self,event):
        self.CoordinateNote1.SetValue(str(self.target_x1) + " " + str(self.target_y1))
        self.CoordinateNote2.SetValue(str(self.target_x2) + " " + str(self.target_y2))

        x1= self.target_x1
        x2= self.target_x2
        y1= self.target_y1
        y2= self.target_y2

        im1_crop=self.im1.crop((x1-(x2-x1)*2,y1-(y2-y1)*2,x2+(x2-x1)*2,y2+(y2-y1)*2))
        im2_crop=self.im2.crop((x1-(x2-x1)*2,y1-(y2-y1)*2,x2+(x2-x1)*2,y2+(y2-y1)*2))
        im3_crop=self.im3.crop((x1-(x2-x1)*2,y1-(y2-y1)*2,x2+(x2-x1)*2,y2+(y2-y1)*2))
        im4_crop=self.im4.crop((x1-(x2-x1)*2,y1-(y2-y1)*2,x2+(x2-x1)*2,y2+(y2-y1)*2))
    
        stitch=Image.new("RGBA",((x2-x1)*10, (y2-y1)*10))
        stitch.paste(im1_crop,(0,0))
        stitch.paste(im2_crop,((x2-x1)*5,0))
        stitch.paste(im3_crop,(0,(y2-y1)*5))
        stitch.paste(im4_crop,((x2-x1)*5,(y2-y1)*5))

        stitch.show()
    def FontSetting(self):
        self.tagsize = int(0.3*abs(self.target_y1-self.target_y2))
        im=Image.new('RGB',(self.tagsize,self.tagsize),(255,0,0))
        txt="1"
        fontsize=30
        font = ImageFont.truetype("arial.ttf", fontsize)
        while font.getsize(txt)[1] < im.size[1]:
            fontsize += 1
            font = ImageFont.truetype("arial.ttf", fontsize)
        self.font=font





    def ListBefore(self,event):
        if self.index == 1:
            return 0

        elif self.index > 1:
            self.index -=1
            self.Note1.SetValue(str(self.L[self.index-1][4]))
            self.Note2.SetValue(str(self.L[self.index][4]))
            self.Note3.SetValue(str(self.L[self.index+1][4]))

            self.Number1 = wx.StaticText(self.panel, -1, str(self.index)+'  ', pos = (5,self.H0+30))
            self.Number2 = wx.StaticText(self.panel, -1, str(self.index+1)+'  ', pos = (5,self.H0+50))
            self.Number3 = wx.StaticText(self.panel, -1, str(self.index+2)+'  ', pos = (5,self.H0+70))

            if (str(self.L[self.index-1][4]))=="None":
                self.saved1 = wx.StaticText(self.panel, -1, "           ", (220,self.H0+30))
                self.Note1.SetValue('')
            if (str(self.L[self.index][4]))=="None":
                 self.saved1 = wx.StaticText(self.panel, -1, "           ", (220,self.H0+50))
                 self.Note2.SetValue('')
            if (str(self.L[self.index+1][4]))=="None":
                 self.saved1 = wx.StaticText(self.panel, -1, "           ", (220,self.H0+70))
                 self.Note3.SetValue('')
            if (str(self.L[self.index-1][4]))!="None":
                self.saved1 = wx.StaticText(self.panel, -1, "Saved!", (220,self.H0+30))

            if (str(self.L[self.index][4]))!="None":
                 self.saved1 = wx.StaticText(self.panel, -1, "Saved!", (220,self.H0+50))

            if (str(self.L[self.index+1][4]))!="None":
                 self.saved1 = wx.StaticText(self.panel, -1, "Saved!", (220,self.H0+70))


##Fixed

    def ListAfter(self,event):
        self.index +=1
        self.Note1.SetValue(str(self.L[self.index-1][4]))
        self.Note2.SetValue(str(self.L[self.index][4]))
        self.Note3.SetValue(str(self.L[self.index+1][4]))

        self.Number1 = wx.StaticText(self.panel, -1, str(self.index)+'  ', pos = (5,self.H0+30))
        self.Number2 = wx.StaticText(self.panel, -1, str(self.index+1)+'  ', pos = (5,self.H0+50))
        self.Number3 = wx.StaticText(self.panel, -1, str(self.index+2)+'  ', pos = (5,self.H0+70))

        if (str(self.L[self.index-1][4]))=="None":
            self.saved1 = wx.StaticText(self.panel, -1, "           ", (220,self.H0+30))
            self.Note1.SetValue('')
        if (str(self.L[self.index][4]))=="None":
             self.saved1 = wx.StaticText(self.panel, -1, "           ", (220,self.H0+50))
             self.Note2.SetValue('')
        if (str(self.L[self.index+1][4]))=="None":
             self.saved1 = wx.StaticText(self.panel, -1, "           ", (220,self.H0+70))
             self.Note3.SetValue('')
        if (str(self.L[self.index-1][4]))!="None":
            self.saved1 = wx.StaticText(self.panel, -1, "Saved!", (220,self.H0+30))

        if (str(self.L[self.index][4]))!="None":
            self.saved1 = wx.StaticText(self.panel, -1, "Saved!", (220,self.H0+50))

        if (str(self.L[self.index+1][4]))!="None":
            self.saved1 = wx.StaticText(self.panel, -1, "Saved!", (220,self.H0+70))







if __name__ == '__main__':
    app = MyGUIApp()
    app.MainLoop()
    app.Quit()
