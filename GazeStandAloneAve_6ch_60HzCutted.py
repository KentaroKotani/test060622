# -*- coding: utf-8 -*-
"""
POLS 視野等表示 ver.9
Stand-alone

"""

#comment 060622
# Import and setting ===========================================================================================
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from sklearn.preprocessing import StandardScaler
import pickle
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
from tkinter import messagebox
import tkinter.simpledialog as simpledialog
from mpl_toolkits.mplot3d import Axes3D
from chardet.universaldetector import UniversalDetector# 文字コード判定
import scipy.signal as sign

fp = FontProperties(fname="c:\\Windows\\Fonts\\YuGothM.ttc")#日本語フォント位置指定

deffont=('Yu Gothic', 20)
# file_name = ""


class ShowViewPointapp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.iconbitmap(self, default="k-lab_logo.ico")
        tk.Tk.wm_title(self, "EOG Gaze Track 3D")

        container = ttk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.frames = {}

        for F in (StartPage, Page3D, Page2D):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        #初期ページレイアウト
        global sf
        style = ttk.Style()
        style.configure('TButton', font=deffont)
        ttk.Frame.__init__(self, parent)

        label = ttk.Label(self, text="CSVファイルを選択してください", font=deffont)
        label.pack(pady=10)

        button0 = ttk.Button(self, text='ファイル選択', style='TButton', command=lambda: self.load_file())
        button0.pack(pady=10, ipadx=10)

        label2 = ttk.Label(self, text="サンプリング間隔", font=deffont)
        label2.pack(pady=10)

        sf = ttk.Spinbox(self, from_=1, to=20, width=5, increment=1, font=deffont)
        sf.pack(pady=10)

        label3 = ttk.Label(self, text="(msec)", font=deffont)
        label3.pack(pady=10)


        button2 = ttk.Button(self, text="3D", command=lambda: controller.show_frame(Page3D))
        button2.pack(pady=10, ipadx=10)
        
        button3 = ttk.Button(self, text="2D", command=lambda: controller.show_frame(Page2D))
        button3.pack(pady=10, ipadx=10)

    def load_file(self):
        global file_name,encode

        file_name = filedialog.askopenfilename(filetypes=[("CSV Files", ".csv")])

        # 文字コード判定------------------------------------
        detector = UniversalDetector()
        fen = open(file_name, mode='rb')
        for binary in fen:
            detector.feed(binary)
            if detector.done:
                break
        detector.close()
        encode=detector.result['encoding']

        self.text = tk.StringVar()#file nameの更新
        self.text.set("%s" % file_name)

        label_path = ttk.Label(self, textvariable=self.text,font=("Yu Gothic", 17))
        label_path.pack(pady=10)


    def sampling_frequency(self):
        sf_values = int(sf.get())
        freq=1000/sf_values
        return freq

   



class Page3D(tk.Frame):

    def __init__(self, parent, controller):
        #3Dページレイアウト
        global  sf, b1, b2, bv1, bv2, b11, b22, bvx1, bvx2, bvy1, bvy2, color1, color2
        '''
        各種変数定義
        bv1, bv2       拡大区間指定用
        bvx1, bvx2     x軸キャリブレーション用
        bvy1, bvy2     y軸キャリブレーション用
        color1, color2 色付け用
        
        '''
        ttk.Frame.__init__(self, parent)

        label = ttk.Label(self, text="位置か速度を選択してください", font=deffont)
        label.grid(pady=10, padx=10, row=0, column=0, columnspan=3)
        
        bv1=tk.StringVar()
        b1 = ttk.Entry(self,width=10, textvariable=bv1)
        b1.insert(tk.END,"0")
        b1.grid(pady=10, padx=10, row=1, column=1)
        
        label00 = ttk.Label(self, text="全体/拡大", font=deffont)
        label00.grid(row=1, column=0)


        

        label1 = ttk.Label(self, text="sec   ~", font=deffont)
        label1.grid(row=1, column=2)
        label2 = ttk.Label(self, text="sec", font=deffont)
        label2.grid(row=1, column=4)
        
        bv2=tk.StringVar()
        b2 = ttk.Entry(self,width=10, textvariable=bv2)
        b2.insert(tk.END,"0")
        b2.grid(pady=10, padx=10, row=1, column=3)
        
        bvx1=tk.StringVar()
        b11 = ttk.Entry(self,width=10, textvariable=bvx1)
        b11.insert(tk.END,"0")
        b11.grid(pady=10, padx=10, row=2, column=1)

        label01=ttk.Label(self, text="x軸キャリブレーション", font=deffont)
        label01.grid(row=2, column=0)
        
        label3 = ttk.Label(self, text="sec  ~", font=deffont)
        label3.grid(row=2, column=2)
        label4 = ttk.Label(self, text="sec", font=deffont)
        label4.grid(row=2, column=4)
        
        bvx2=tk.StringVar()
        b22 = ttk.Entry(self,width=10, textvariable=bvx2)
        b22.insert(tk.END,"0")
        b22.grid(pady=10, padx=10, row=2, column=3)


        label02=ttk.Label(self, text="y軸キャリブレーション", font=deffont)
        label02.grid(row=3, column=0)

        bvy1=tk.StringVar()
        by1 = ttk.Entry(self,width=10, textvariable=bvy1)
        by1.insert(tk.END,"0")
        by1.grid(pady=10, padx=10, row=3, column=1)
        
        label3 = ttk.Label(self, text="sec  ~", font=deffont)
        label3.grid(row=3, column=2)
        label4 = ttk.Label(self, text="sec", font=deffont)
        label4.grid(row=3, column=4)
        
        bvy2=tk.StringVar()
        by2 = ttk.Entry(self,width=10, textvariable=bvy2)
        by2.insert(tk.END,"0")
        by2.grid(pady=10, padx=10, row=3, column=3)


        label03=ttk.Label(self, text="色付け", font=deffont)
        label03.grid(row=4, column=0)

        color1=tk.StringVar()
        but1=ttk.Entry(self, width=10, textvariable=color1)
        but1.insert(tk.END, "0")
        but1.grid(pady=10, padx=10, row=4, column=1)

        label5 = ttk.Label(self, text="sec  ~", font=deffont)
        label5.grid(row=4, column=2)
        label6 = ttk.Label(self, text="sec", font=deffont)
        label6.grid(row=4, column=4)

        color2=tk.StringVar()
        but2=ttk.Entry(self, width=10, textvariable=color2)
        but2.insert(tk.END, "0")
        but2.grid(pady=10, padx=10, row=4, column=3)

        button1 = ttk.Button(self, text='位置', style='TButton', command=lambda: self.gaze_3d())
        button1.grid(pady=10, padx=10, row=5, column=0, columnspan=3)
        
        button3 = ttk.Button(self, text='速度', style='TButton', command=lambda: self.gaze_v())
        button3.grid(pady=10, padx=10, row=6, column=0, columnspan=3)

        button2 = ttk.Button(self, text="戻る", command=lambda: controller.show_frame(StartPage))
        button2.grid(pady=10, padx=10, row=7, column=0, columnspan=3)
    
    def spin_values(self):
        #拡大区間[s]推定モジュール
        b1_values = float(bv1.get())
        b2_values = float(bv2.get())
        print(b1_values)
        print(b2_values)
        return b1_values, b2_values
        
    def spin_values2(self):
        #x軸キャリブレーションモジュール
        b11_values = float(bvx1.get())
        b22_values = float(bvx2.get())
        print(b11_values)
        print(b22_values)
        return b11_values, b22_values

    def spin_values3(self):
        #y軸キャリブレーションモジュール
        by1_values = float(bvy1.get())
        by2_values = float(bvy2.get())
        print(by1_values)
        print(by2_values)
        return by1_values, by2_values

    def spin_values_col(self):
        #色付けモジュール
        b1_values = float(color1.get())
        b2_values = float(color2.get())
        print(b1_values)
        print(b2_values)
        return b1_values, b2_values

    def driftcut(self, verR):
        #ドリフト(線形ノイズ)カットアルゴリズムモジュール
        maxidx=sign.argrelmax(verR, order=100) #サッケードの極大，極小値の要素数を出す
        minidx=sign.argrelmin(verR, order=100)
        cut_ver=np.hstack([maxidx, minidx])
        cut_ver=np.sort(cut_ver)              #極大，極小二つを合わせて並べ替え
        SCpeak=np.array([0])
        
        for j in range(len(cut_ver[0, :])):
            pi=verR[cut_ver[0, j]]
            if ((pi>0.1) or (pi<-0.1)):
               SCpeak=np.append(SCpeak, cut_ver[0, j])
            
        SCpeak=np.append(SCpeak, len(verR)-1)
        
        for i in range(len(SCpeak)-1):
            #固視区間抽出
            #収録開始, 終了時間とサッケードピークを分けるif関数-----
            if (SCpeak[i]==0):
                AVstart=0
            else:
                AVstart=SCpeak[i]+150

            if (SCpeak[i+1]==(len(verR)-1)):
                AVend=SCpeak[i+1]
            else:
                AVend=SCpeak[i+1]-50
            #-------------------------------------------------------

            AVEverR=verR[AVstart:AVend] #固視区間のデータを抜き出す
            verR[AVstart:AVend]=verR[AVstart:AVend]-(np.average(AVEverR)) #抜き出したデータから平均値を出し，固視区間から引く
            
        fig=plt.figure()
        ax1=fig.add_subplot(111)
        ax1.plot(verR)
        print(SCpeak)
        return verR
    

    def gaze_3d(self):
        #位置データ3D出力

        if file_name == "":
            sub_win = tk.Toplevel()
            tk.Message(sub_win, aspect=1000, text="CSVファイルを選択してください",
                       font=deffont).pack(pady=10, padx=10)

        else:
            signal = np.loadtxt("%s" % file_name, skiprows=11, usecols=(0, 1, 2, 3), delimiter=",", encoding=encode)
            # signal = np.loadtxt("%s" % file_name, skiprows=1, delimiter=",", encoding="utf-8")
            # signal = np.loadtxt("%s" %file_name, skiprows=1, delimiter=",")
            # 　csv ファイルを行列式として読み込む（utf-8形式）
            vsignal=signal*(10-(-10))/65536+(-10)
            #　読み込んだデータを分解能⇒電位[v]に変換
            
            samplingfreq =StartPage.sampling_frequency(self)
            
            box11, box22=self.spin_values2()
            cbox11=int(box11*samplingfreq)
            cbox22=int(box22*samplingfreq)
            
            #キャリブレーション用
            if (cbox22 != 0):
               #x軸
               deg15x=abs(np.sum(vsignal[cbox11:cbox22, 0]))
               cdlx=15/deg15x
               
            else :
               
               cdlx=1

            boxy1,boxy2=self.spin_values3()
            cboxy1=int(boxy1*samplingfreq)
            cboxy2=int(boxy2*samplingfreq)

            if (cbox22 != 0):
               #y軸
               deg15y=abs(np.sum(vsignal[cbox11:cbox22, 1]))
               cdly=15/deg15y

            else :
                cdly=1

            """
            Memo -------------------------------------------------------------------------------------------------
            signal:
            0=No,1=Idx_Raw,2=テーブル番号,3=絶対位置X,4=絶対位置Y,5=表示状態,6=状態連番,
            7=信号Ch0(水平信号(左眼反転)),8=信号(Ch1垂直信号(mV)),9=信号Ch2(水平眼位(左眼反転)),10=信号Ch3(垂直眼位)
            ------------------------------------------------------------------------------------------------------
            """
            (t, s) = signal.shape  # 行列数表示: t=行数(時間データ),s=列数(計測項目データ)
            
            
            stime = np.arange(t) / samplingfreq  # 検査時間(sec)
            #kf = KalmanFilter(transition_matrices=np.array([[1, 1], [0, 1]]),transition_covariance=0.0000001*np.eye(2))

            # ドリフトカット(右目) --------------------------------------------------------------------
            
            verxR=Page2D.bandstop(self,(vsignal[:, 0]), samplingfreq)
            q=len(verxR)
            
            #ver_xxR=kf.em(ver_xR).filter(ver_xR)[0]
            veryR=Page2D.bandstop(self,(vsignal[:, 1]), samplingfreq)
            #ver_yyR=kf.em(ver_yR).filter(ver_yR)[0]
            #verxx=Page2D.Threshold(self,verx)
            #veryy=Page2D.Threshold(self,very)
            
            box1, box2= self.spin_values()
            cbox1=int(box1*samplingfreq)
            cbox2=int(box2*samplingfreq)

            col1, col2 = self.spin_values_col()
            ccol1=int(col1*samplingfreq)
            ccol2=int(col2*samplingfreq)
      

            # ドリフトカット(左目) --------------------------------------------------------------------
            
            verxL=Page2D.bandstop(self,(vsignal[:, 2]), samplingfreq)
            #ver_xxL=kf.em(ver_xL).filter(ver_xL)[0]
            veryL=Page2D.bandstop(self,(vsignal[:, 3]), samplingfreq)
            #ver_yyL=kf.em(ver_yL).filter(ver_yL)[0]
            #verxx=Page2D.Threshold(self,verx)
            #veryy=Page2D.Threshold(self,very)
            

            # 拡大（両目)--------------------------------------------------------------------
            if (0<=cbox1) and (cbox1 < t):
             startidx=cbox1
            else:
             startidx=0
            
            if (box2 <= box1):
             endidx=t
            elif (cbox2>0) and (cbox2<=t):
             endidx=cbox2
            else:
             endidx=t

            ver_xR=self.driftcut(verxR)
            ver_yR=self.driftcut(veryR)
            ver_xL=self.driftcut(verxL)
            ver_yL=self.driftcut(veryL)
             
            pos_xR = (np.cumsum(ver_xR[startidx:endidx]))*cdlx
            pos_yR = (np.cumsum(ver_yR[startidx:endidx]))*cdly
            pos_xL = (np.cumsum(ver_xL[startidx:endidx]))*cdlx
            pos_yL = (np.cumsum(ver_yL[startidx:endidx]))*cdly

            # plot(二次元)-----------------------------------------------------------------^
            figp1=plt.figure()
            axp1=figp1.add_subplot(111)
            axp1.plot(pos_xR)

            figp2=plt.figure()
            axp2=figp2.add_subplot(111)
            axp2.plot(pos_yR)
            
            figp3=plt.figure()
            axp3=figp3.add_subplot(111)
            axp3.plot(pos_xL)

            figp4=plt.figure()
            axp4=figp4.add_subplot(111)
            axp4.plot(pos_yL)




            # plot(右目)--------------------------------------------------------------------

            plt.style.use("seaborn")
            fig = plt.figure(figsize=(10, 9))
            ax = Axes3D(fig)
            ax.plot(stime[startidx:endidx], pos_xR, pos_yR, ".-", 
                    label="Eye Movement")
            if (ccol1!=0):
                ax.plot(stime[ccol1:ccol2], pos_xR[ccol1-startidx:ccol2-startidx], pos_yR[ccol1-startidx:ccol2-startidx], ".-")
            
            #ax.set_zlim(-25,75)
            #ax.set_ylim(-25,75)
            ax.set_xlabel("time(sec)")
            ax.set_ylabel("x Eye Position[deg]")
            ax.set_zlabel("y Eye Position[deg]")

             # plot(左目)--------------------------------------------------------------------

            plt.style.use("seaborn")
            figL = plt.figure(figsize=(10, 9))
            axL = Axes3D(figL)
            axL.plot(stime[startidx:endidx], pos_xL, pos_yL, ".-", 
                    label="Eye Movement")
            if (ccol1!=0):
                axL.plot(stime[ccol1:ccol2], pos_xL[ccol1-startidx:ccol2-startidx], pos_yL[ccol1-startidx:ccol2-startidx], ".-")
            #axL.set_zlim(-25, 75)
            #axL.set_ylim(-25, 75)
            axL.set_xlabel("time(sec)")
            axL.set_ylabel("x Eye Position[deg]")
            axL.set_zlabel("y Eye Position[deg]")
            plt.grid()
            plt.show()

            
    def gaze_v(self):

        if file_name == "":
            sub_win = tk.Toplevel()
            tk.Message(sub_win, aspect=1000, text="CSVファイルを選択してください",
                       font=deffont).pack(pady=10, padx=10)

        else:
            signal = np.loadtxt("%s" % file_name, skiprows=11, usecols=(0, 1, 2, 3), delimiter=",", encoding=encode)
            # signal = np.loadtxt("%s" % file_name, skiprows=1, delimiter=",", encoding="utf-8")
            # signal = np.loadtxt("%s" %file_name, skiprows=1, delimiter=",")
            # 　csv ファイルを行列式として読み込む（utf-8形式）
            vsignal=signal*(10-(-10))/65536+(-10)

            """
            Memo -------------------------------------------------------------------------------------------------
            signal:
            0=No,1=Idx_Raw,2=テーブル番号,3=絶対位置X,4=絶対位置Y,5=表示状態,6=状態連番,
            7=信号Ch0(水平信号(左眼反転)),8=信号(Ch1垂直信号(mV)),9=信号Ch2(水平眼位(左眼反転)),10=信号Ch3(垂直眼位)
            ------------------------------------------------------------------------------------------------------
            """
            (t, s) = signal.shape  # 行列数表示: t=行数(時間データ),s=列数(計測項目データ)
            
            samplingfreq =StartPage.sampling_frequency(self)
            stime = np.arange(t) / samplingfreq  # 検査時間(sec)
            
            # ドリフトカット(右目) --------------------------------------------------------------------
            
            verxR=Page2D.bandstop(self,(vsignal[:, 0]), samplingfreq)
            q=len(verxR)
            ver_xR=self.driftcut(verxR)
            veryR=Page2D.bandstop(self,(vsignal[:, 1]), samplingfreq)
            ver_yR=self.driftcut(veryR)
            #verxx=Page2D.Threshold(self,verx)
            #veryy=Page2D.Threshold(self,very)
            
            box1, box2= self.spin_values()
            cbox1=int(box1*samplingfreq)
            cbox2=int(box2*samplingfreq)

            col1, col2 = self.spin_values_col()
            ccol1=int(col1*samplingfreq)
            ccol2=int(col2*samplingfreq)
           
            # 拡大（右目)--------------------------------------------------------------------
            if (0<=cbox1) and (cbox1 < t):
             startidx=cbox1
            else:
             startidx=0
            
            if (box2 <= box1):
             endidx=t
            elif (cbox2>0) and (cbox2<=t):
             endidx=cbox2
            else:
             endidx=t
             
             
            # plot(右目)--------------------------------------------------------------------
            
            plt.style.use("seaborn")
            fig = plt.figure(figsize=(10, 9))
            ax = Axes3D(fig)
            ax.plot(stime[startidx:endidx], ver_xR, ver_yR, ".-", 
                    label="Eye Movement")
            if (ccol1!=0):
                ax.plot(stime[ccol1:ccol2], ver_xR[ccol1-startidx:ccol2-startidx], ver_yR[ccol1-startidx:ccol2-startidx], ".-")

            ax.set_xlabel("time(sec)")
            ax.set_ylabel("x Eye Position[deg]")
            ax.set_zlabel("y Eye Position[deg]")
            
            
           
            '''
            res = tk.messagebox.askquestion("csvファイルの保存","位相データを.csvファイルとして保存しますか?")
            if res =="yes":
                inputdata = simpledialog.askstring("ファイル名","ファイル名を入力")
                np.savetxt(str(inputdata)+".csv", pos, delimiter=",")
            '''

           

            """
            Memo -------------------------------------------------------------------------------------------------
            signal:
            0=No,1=Idx_Raw,2=テーブル番号,3=絶対位置X,4=絶対位置Y,5=表示状態,6=状態連番,
            7=信号Ch0(水平信号(左眼反転)),8=信号(Ch1垂直信号(mV)),9=信号Ch2(水平眼位(左眼反転)),10=信号Ch3(垂直眼位)
            ------------------------------------------------------------------------------------------------------
            """
            
            

            # ドリフトカット(左目) --------------------------------------------------------------------
            
            verxL=Page2D.bandstop(self,(vsignal[:, 2]), samplingfreq)
            q=len(verxR)
            ver_xL=self.driftcut(verxL)
            veryL=Page2D.bandstop(self,(vsignal[:, 3]), samplingfreq)
            ver_yL=self.driftcut(veryL)
            #verxx=Page2D.Threshold(self,verx)
            #veryy=Page2D.Threshold(self,very)

             # plot(左目)--------------------------------------------------------------------

            plt.style.use("seaborn")
            figL = plt.figure(figsize=(10, 9))
            axL = Axes3D(figL)
            axL.plot(stime[startidx:endidx], ver_xL, ver_yL, ".-", 
                    label="Eye Movement")
            if (ccol1!=0):
                axL.plot(stime[ccol1:ccol2], ver_xL[ccol1-startidx:ccol2-startidx], ver_yL[ccol1-startidx:ccol2-startidx], ".-")
            axL.set_xlabel("time(sec)")
            axL.set_ylabel("x Eye Position[deg]")
            axL.set_zlabel("y Eye Position[deg]")
            plt.grid()
            plt.show()


class Page2D(tk.Frame):
    #2Dグラフ出力

    def __init__(self, parent, controller):
        #2Dページレイアウト
        global  sf, b1, b2, bv3, bv4
        ttk.Frame.__init__(self, parent)

        label = ttk.Label(self, text="検出データを選択してください", font=deffont)
        label.grid(pady=10, padx=10, row=0, column=0, columnspan=3)
        
        bv3=tk.StringVar()
        b1=ttk.Entry(self, width=10, textvariable=bv3)
        b1.insert(tk.END,"0")
        b1.grid(pady=10, padx=10, row=1, column=0)

        label1 = ttk.Label(self, text="~", font=deffont)
        label1.grid(row=1, column=1)
        
        bv4=tk.StringVar()
        b2=ttk.Entry(self, width=10, textvariable=bv4)
        b2.insert(tk.END,"0")
        b2.grid(pady=10, padx=10, row=1, column=2)

        button1 = ttk.Button(self, text='位置および速度', style='TButton', command=lambda: self.gaze_2dpha())
        button1.grid(pady=10, padx=10, row=3, column=0, columnspan=3)
        
        button3 = ttk.Button(self, text='fft', style='TButton', command=lambda: self.gaze_2dver())
        button3.grid(pady=10, padx=10, row=4, column=0, columnspan=3)

        button2 = ttk.Button(self, text="戻る", command=lambda: controller.show_frame(StartPage))
        button2.grid(pady=10, padx=10, row=5, column=0, columnspan=3)
     
    def spin_values(self):
        b1_values = float(bv3.get())
        b2_values = float(bv4.get())
        print(bv3.get)
        print(bv4.get)
        print(b1_values)
        print(b2_values)
        return b1_values, b2_values
        
    def bandstop(self,ssignal,smprate):
        N=1
        F=np.array([59,61])
        b,a=sign.butter(N,F,"bandstop", fs=smprate)
        y=sign.filtfilt(b,a,ssignal)
        return y
        #N=1
        #F=60
        #b,a=sign.butter(N,F,"low", fs=smprate)
        #y=sign.filtfilt(b,a,ssignal)
        #return y

    def highpass(self, x, smprate):
        N=1
        F=0.06
        Fs=smprate
        b, a=sign.butter(N, F, "high", fs=Fs)
        y=sign.filtfilt(b,a,x)
        return y
    
    def highpassl(self, x, smprate):
        N=1
        F=0.02
        Fs=smprate
        b, a=sign.butter(N, F, "high", fs=Fs)
        y=sign.lfilter(b,a,x)
        return y
        
    def Threshold(self, ver):
        #　posx,yを昇順にソートし、(値-中央値)²を行っている
        e1=np.sort(ver)           
        e3=np.square(e1-np.median(e1))          
        # 標準偏差から閾値を計算
        q=len(e1)           
        thres=2*(np.sqrt((np.sum(e3))/q))          
        return thres
        
    def MS_detector(self, vero):
        #Engbert(2003)の手順を再現する関数
        v1=np.median(np.sort(np.square(vero))) #速度の二乗の中央値
        v2=np.square(np.median(np.sort(vero))) #速度の中央値の二乗
        
        sigma=v1-v2 #Engbert(2003)の(2)式
        
        eta=13*sigma #Engbert(2003)の(3)式
        return eta

    def gaze_2dpha(self):
        
        if file_name == "":
            sub_win = tk.Toplevel()
            tk.Message(sub_win, aspect=1000, text="CSVファイルを選択してください",
                       font=deffont).pack(pady=10, padx=10)

        else:
            signal = np.loadtxt("%s" % file_name, skiprows=11, usecols=(0 ,1, 2, 3), delimiter=",", encoding=encode)
            # signal = np.loadtxt("%s" % file_name, skiprows=1, delimiter=",", encoding="utf-8")
            # signal = np.loadtxt("%s" %file_name, skiprows=1, delimiter=",")
            # 　csv ファイルを行列式として読み込む（utf-8形式）
            vsignal=signal*(10-(-10))/65536+(-10)
            
            (t, s) = signal.shape  # 行列数表示: t=行数(時間データ),s=列数(計測項目データ)
            
            samplingfreq =StartPage.sampling_frequency(self)
            stime = np.arange(t) / samplingfreq  # 検査時間(sec)
           
            
            """
            Memo -------------------------------------------------------------------------------------------------
            signal:
            0=No,1=Idx_Raw,2=テーブル番号,3=絶対位置X,4=絶対位置Y,5=表示状態,6=状態連番,
            7=信号Ch0(水平信号(左眼反転)),8=信号(Ch1垂直信号(mV)),9=信号Ch2(水平眼位(左眼反転)),10=信号Ch3(垂直眼位)
            ------------------------------------------------------------------------------------------------------
            """
           # ドリフトカット(右目) --------------------------------------------------------------------
            
            verxR=self.bandstop((vsignal[:, 0]), samplingfreq)
            q=len(verxR)
            
            #ver_xxR=kf.em(ver_xR).filter(ver_xR)[0]
            veryR=self.bandstop((vsignal[:, 1]), samplingfreq)
            #ver_yyR=kf.em(ver_yR).filter(ver_yR)[0]
            #verxx=Page2D.Threshold(self,verx)
            #veryy=Page2D.Threshold(self,very)
            
            box1, box2= self.spin_values()
            cbox1=int(box1*samplingfreq)
            cbox2=int(box2*samplingfreq)

     

            # ドリフトカット(左目) --------------------------------------------------------------------
            
            verxL=self.bandstop((vsignal[:, 2]), samplingfreq)
            #ver_xxL=kf.em(ver_xL).filter(ver_xL)[0]
            veryL=self.bandstop((vsignal[:, 3]), samplingfreq)
            #ver_yyL=kf.em(ver_yL).filter(ver_yL)[0]
            #verxx=Page2D.Threshold(self,verx)
            #veryy=Page2D.Threshold(self,very)
            

            # 拡大（両目)--------------------------------------------------------------------
            if (0<=cbox1) and (cbox1 < t):
             startidx=cbox1
            else:
             startidx=0
            
            if (box2 <= box1):
             endidx=t
            elif (cbox2>0) and (cbox2<=t):
             endidx=cbox2
            else:
             endidx=t

             
            pos_xR = (np.cumsum(verxR[startidx:endidx]))
            pos_yR = (np.cumsum(veryR[startidx:endidx]))
            pos_xL = (np.cumsum(verxL[startidx:endidx]))
            pos_yL = (np.cumsum(veryL[startidx:endidx]))

            # plot(二次元)-----------------------------------------------------------------^
            figp=plt.figure()
            axp=figp.add_subplot(111)
            axp.plot(stime[startidx:endidx], pos_xR, color='blue', label='Right_H')

            axp.plot(stime[startidx:endidx], pos_yR, color='red', label='Right_V')
            
            axp.plot(stime[startidx:endidx], pos_xL, color='green', label='Left_H')

            axp.plot(stime[startidx:endidx], pos_yL, color='cyan', label='Left_V')
            plt.title('position')
            plt.legend()
            plt.grid()

            figv=plt.figure()
            axv=figv.add_subplot(111)
            axv.plot(stime, verxR, color='blue', label='Right_H')

            axv.plot(stime, veryR, color='red', label='Right_V')
            
            axv.plot(stime, verxL, color='green', label='Left_H')

            axv.plot(stime, veryL, color='cyan', label='Left_V')
            plt.title('verocity')
            plt.legend()
            plt.grid()
            plt.show()
            
    def gaze_2dver(self):
        
        if file_name == "":
            sub_win = tk.Toplevel()
            tk.Message(sub_win, aspect=1000, text="CSVファイルを選択してください",
                       font=deffont).pack(pady=10, padx=10)

        else:
            signal = np.loadtxt("%s" % file_name, skiprows=11, usecols=(0,1), delimiter=",", encoding=encode)
            # signal = np.loadtxt("%s" % file_name, skiprows=1, delimiter=",", encoding="utf-8")
            # signal = np.loadtxt("%s" %file_name, skiprows=1, delimiter=",")
            # 　csv ファイルを行列式として読み込む（utf-8形式）
            vsignal=signal*(10-(-10))/65536+(-10)
            
            (t, s) = signal.shape  # 行列数表示: t=行数(時間データ),s=列数(計測項目データ)
            samplingfreq =StartPage.sampling_frequency(self)
            stime = np.arange(t) / samplingfreq  # 検査時間(sec)
                       
           
                       
            """
            Memo -------------------------------------------------------------------------------------------------
            signal:
            0=No,1=Idx_Raw,2=テーブル番号,3=絶対位置X,4=絶対位置Y,5=表示状態,6=状態連番,
            7=信号Ch0(水平信号(左眼反転)),8=信号(Ch1垂直信号(mV)),9=信号Ch2(水平眼位(左眼反転)),10=信号Ch3(垂直眼位)
            ------------------------------------------------------------------------------------------------------
            """
            
            
            

            # FFT --------------------------------------------------------------------
            fft_sig = np.fft.fft(vsignal[:, 0], axis=0)  # X軸Y軸それぞれに対してFFT
            freq = np.fft.fftfreq(stime, d=(1 / samplingfreq))
            ifft_sig = np.real(np.fft.ifft(fft_sig, axis=0))
            sig_ampx = (np.abs(fft_sig))  # fft結果を絶対値に変換
            posx_amp=sig_ampx/t*2
           
            
        
            #plot--------------------------------------------------------------------
            fig=plt.figure()
            ax=fig.add_subplot(111)
            ax.plot(freq[:int(t/2)], posx[:int(t/2)], label='Eye Movement')
            ax.set_xlabel("frequency [Hz]")
            ax.set_ylabel("amplitude")
            #ax.set_xlim(0,10)
            plt.legend(loc="best")
            plt.show()
            """
            res = tk.messagebox.askquestion("csvファイルの保存","位相データを.csvファイルとして保存しますか?")
            if res =="yes":
                inputdata = simpledialog.askstring("ファイル名","ファイル名を入力")
                np.savetxt(str(inputdata)+".csv", pos, delimiter=",")
            """
    
     
            
           



app = ShowViewPointapp()
app.mainloop()
