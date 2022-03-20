import json
import os
import sys
from kivy.resources import resource_add_path, resource_find
from kivy.core.text import LabelBase
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from xyw import xywlogin, xywlogout, whatstatus

PATH = os.path.dirname(os.path.realpath(sys.argv[0]))

# 网络连通状态 全局变量
STATUS = False

resource_add_path(PATH + '/units')
LabelBase.register('Roboto', 'msyhl.ttc')


class MyGrid(GridLayout):
    # 初始化
    def __init__(self, **kwargs):
        global STATUS

        try:
            with open(f'{PATH}/.temp/config.json', 'r') as f:
                cfgdict = json.load(f)
        except json.decoder.JSONDecodeError:
            cfgdict = {"username": "", "password": "", "ispcode": ""}

        super(MyGrid, self).__init__(**kwargs)
        self.cols = 1

        self.inside = GridLayout()
        self.inside.cols = 2
        
        self.inin = GridLayout()
        self.inin.cols = 1

        STATUS = whatstatus()

        if STATUS:
            self.status = Label(text="[b][color=5bae23]网络已连通[/color][/b]", font_size=40, markup=True)
        else:
            self.status = Label(text="[b][color=de1c31]网络未连通[/color][/b]", font_size=40, markup=True)
        self.add_widget(self.status)

        self.inside.add_widget(Label(text="学号: ", font_size=25))
        self.username = TextInput(multiline=False)
        self.username.text = cfgdict["username"]
        self.inside.add_widget(self.username)

        self.inside.add_widget(Label(text="密码: ", font_size=25))
        self.password = TextInput(multiline=False)
        if cfgdict["password"] != "":
            self.pwcache = cfgdict["password"]
            self.password.text = '*******'
        else:
            self.password.text = ""
            self.pwcache = ""
        self.inside.add_widget(self.password)

        self.inside.add_widget(Label(text="运营商(电信/移动/联通/教职工):\n不填此栏默认为校内网 ", font_size=25))
        self.ispname = TextInput(multiline=False)
        self.ispname.text = cfgdict["ispcode"]
        self.inside.add_widget(self.ispname)

        self.add_widget(self.inside)

        self.submit = Button(text="登入", font_size=40)
        self.submit.bind(on_press=self.loginpressed)
        self.inin.add_widget(self.submit)

        self.logout = Button(text="登出", font_size=40)
        self.logout.bind(on_press=self.logoutpressed)
        self.inin.add_widget(self.logout)

        self.save = Button(text="保存", font_size=40)
        self.save.bind(on_press=self.savepressed)
        self.inin.add_widget(self.save)

        self.clean = Button(text="清空", font_size=40)
        self.clean.bind(on_press=self.cleanpressed)
        self.inin.add_widget(self.clean)

        self.add_widget(self.inin)


    # 登入按钮
    def loginpressed(self, instance):
        global STATUS

        self.pwcover()
        form = {"username":self.username.text,"password":self.pwcache,"ispcode":self.ispname.text}
        if form["username"] == "" or form["password"] == "":
            self.status.text = "[color=de1c31]请输入学号和密码[/color]"
        elif self.chkname():
            self.username.text = ""
            self.status.text = "[color=de1c31]请输入正确的学号[/color]"
        else:
            if form["ispcode"] != "":
                # 教职工: @jzg  电信: @aust  联通: @unicom  移动: @cmcc  校内: 留空
                ispdict = {"\u6559\u804c\u5de5":"@jzg", "\u7535\u4fe1":"@aust", "\u8054\u901a":"@unicom", "\u79fb\u52a8":"@cmcc"}

                if form["ispcode"] in ispdict:
                    form["ispcode"] = ispdict[form["ispcode"]]
                    STATUS = xywlogin(**form, PATH=PATH)
                    self.oputstatus("网络已连通", "网络未连通", STATUS)
                else:
                    self.ispname.text = ""
                    self.status.text = "[color=de1c31]请输入正确的运营商名称\n电信/移动/联通/教职工[/color]"        
            else:
                STATUS = xywlogin(**form, PATH=PATH)
                self.oputstatus("网络已连通", "网络未连通", STATUS)


    # 登出按钮
    def logoutpressed(self, instance):
        global STATUS

        self.pwcover()
        form = {"username":self.username.text,"password":self.pwcache,"ispcode":self.ispname.text}
        if form["username"] == "":
            self.status.text = "[color=de1c31]请输入学号[/color]"
        elif self.chkname():
            self.username.text = ""
            self.status.text = "[color=de1c31]请输入正确的学号[/color]"
        else:
            try:
                with open(f'{PATH}/.temp/.cache', 'r') as f:
                    cachedict = json.load(f)
                STATUS = xywlogout(form["username"], cachedict)
                if STATUS:
                    self.status.text = "[color=de1c31]登出失败,请检查学号[/color]"                
                else:
                    self.status.text = "[b][color=de1c31]网络未连通[/color][/b]"
            except json.decoder.JSONDecodeError:
                cachedict = {"current_user_agent": "", "macid": "", "v46ip": ""}
                

    # 保存按钮
    def savepressed(self, instance):
        self.pwcover()
        form = {"username":self.username.text,"password":self.pwcache,"ispcode":self.ispname.text}
        cfgdict = {}

        if form["username"] == "":
            self.status.text = "[color=de1c31]至少输入学号才可以保存哦[/color]"
        elif self.chkname():
            self.username.text = ""
            self.status.text = "[color=de1c31]请输入正确的学号[/color]"
        else:
            if form["ispcode"] != "":
                # 教职工: \u6559\u804c\u5de5  电信: \u7535\u4fe1  联通: \u8054\u901a  移动: \u79fb\u52a8  校内: 无
                isplist = ["\u6559\u804c\u5de5","\u7535\u4fe1","\u8054\u901a","\u79fb\u52a8"]

                if form["ispcode"] in isplist or form["ispcode"] == None:
                    cfgdict = form
                    with open(f'{PATH}/.temp/config.json', 'w') as f:
                        json.dump(cfgdict, f)

                    self.oputstatus("网络已连通(保存完成)", "网络未连通(保存完成)", STATUS)

                else:
                    self.ispname.text = ""
                    self.status.text = "[color=de1c31]请输入正确的运营商名称[/color]"
        
            else:
                cfgdict = form
                with open(f'{PATH}/.temp/config.json', 'w') as f:
                    json.dump(cfgdict, f)

                self.oputstatus("网络已连通(保存完成)", "网络未连通(保存完成)", STATUS)
            
          
    # 清空按钮 清空面板与储存的配置
    def cleanpressed(self, instance):
        global STATUS

        with open(f'{PATH}/.temp/config.json', 'w') as f:
            f.write('')
        
        self.username.text = ""
        self.password.text = ""
        self.cache = ""
        self.ispname.text = ""

        self.oputstatus("网络已连通(清空完成)", "网络未连通(清空完成)", STATUS)


    # 显示网络状态
    def oputstatus(self, textone, texttwo, networkstatus):
        if networkstatus:
            self.status.text = f"[b][color=5bae23]{textone}[/color][/b]"
        else:
            self.status.text = f"[b][color=de1c31]{texttwo}[/color][/b]"


    # 检查学工号是否符合规范
    def chkname(self) -> bool:
        username = int(self.username.text)
        if (username >= 2016000000 and username <= 2100000000) or (username >= 1900000 and username <= 2100000):
            return False
        return True


    # 密码遮盖
    def pwcover(self):
        if self.password.text != '*******' and self.password.text != "":
            self.pwcache = self.password.text
            self.password.text = '*******'


class MyApp(App):
    def build(self):
        return MyGrid()


if __name__ == "__main__":
    MyApp().run()