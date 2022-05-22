import re
files =["file.txt","serverFile.txt"] #,""
for filename in files:
    f = open(filename, "r")
    count=0
    for line in f:
        line = line.strip()
        if(line!=""):
            count+=1
    f.close()
    f=open(filename, "r")
    txt=""
    count2=0
    unlock = False
    for row in f:
        if(count2==0):
            pass
        if not unlock:
            match=re.findall(r'(Interval\s*Transfer\s*Bitrate\s* Total\s*Datagrams|Interval\s*Transfer\s*Bitrate\s*Jitter\s*Lost/Total Datagrams)', row)
            if match:
                unlock=True
        if unlock:
            if(count2<count-4):
                row = row.strip()
                match = re.findall(r'(\[\s+\d\]|\[\s\w+\])', row)
                if(match):
                    if(match[0]!="[ ID]"):
                        row=row.replace(match[0], "")
                        row=row.replace("sec", "")
                        row=row.replace("ms", "")
                        row=row.replace("/", "")
                        row=row.strip()
                        row=" ".join(row.split())
                        lines=row.split(" ")
                        if(lines[2]=="KBytes"): #clean columns 2 and 3
                            lines[1]=str(float(lines[1])*1024*8)
                        if(lines[2]=="MBytes"): 
                            lines[1]=str(float(lines[1])*1024*1024*8)
                        lines[2]=""
                        if(lines[4]=="Mbits"):
                            lines[3]=str(float(lines[3])*1e6)
                        if(lines[4]=="Kbits"):
                            lines[3]=str(float(lines[3])*1e3)
                        lines[4]=""
                        row=" ".join(lines)
                        row=" ".join(row.split())
                        row=row.replace(" ",",")
                    else:
                        row=row.replace(match[0], "")
                        row=" ".join(row.split())
                        row=row.replace(" ", ",")
                if(row!="- - - - - - - - - - - - - - - - - - - - - - - - -"):
                    txt+=row+"\n"
        count2+=1
    f2=open(filename.split(".")[0]+".csv", "w")
    f2.write(txt)
    f2.close()
