# 服务器上面的python环境用的是本地的，没有创建虚拟环境。
# https://blog.csdn.net/m0_59092234/article/details/126041386

# 给wtt做的考勤

# 在mac上测试和在linux上使用需要更改两个地方，第一个，python这个command；第二个，application.yml中的file-save-path这个路径。

# 需要把python文件上传到：
# scp /Users/dinosaur/jcwang/IDEA/WTT_kaoqin/wtt_kaoqin_python/wtt_gongzuobiao_new.py ubuntu@43.142.73.10:/home/ubuntu/wtt_kaoqin
# scp /Users/dinosaur/jcwang/IDEA/WTT_kaoqin/wtt_kaoqin_python/wtt_gongzuobiao_old.py ubuntu@43.142.73.10:/home/ubuntu/wtt_kaoqin

# 需要把这个java包上传到：
# scp /Users/dinosaur/jcwang/IDEA/WTT_kaoqin/target/WTT_kaoqin-0.0.1-SNAPSHOT.jar ubuntu@43.142.73.10:/home/ubuntu/wtt_kaoqin

# 然后运行jar包：nohup java -jar /home/ubuntu/wtt_kaoqin/WTT_kaoqin-0.0.1-SNAPSHOT.jar >/home/ubuntu/wtt_kaoqin/temp_log.txt &

# 查看日志： cat /home/ubuntu/wtt_kaoqin/temp_log.txt

# ps -ef | grep java

# http://43.142.73.10:10007/upload/wtt_gongzuobiao_new
# http://43.142.73.10:10007/upload/wtt_gongzuobiao_old

# source /Users/dinosaur/jcwang/pythonvenv/venvpaper39/bin/activate
# pip install chinesecalendar  #默认安装是最新版版的1.6.1
# 



 
# 或者在判断的同时，获取节日名
import chinese_calendar as calendar
from chinese_calendar import is_workday



# import datetime
 
# # 判断指定日期,如：2015年9月3日 是不是节假日
# data = datetime.date(2015, 9, 3)
# if is_workday(data):
#   print("是工作日")
# else:
#   print("是节假日")
 
# # 或者在判断的同时，获取节日名
# import chinese_calendar as calendar
# on_holiday, holiday_name = calendar.get_holiday_detail(data)
# if on_holiday:
#   print('是节假日')
# else:
#   print('是工作日')
# if holiday_name in ["New Year's Day","Spring Festival","Tomb-sweeping Day","Labour Day","Dragon Boat Festival","National Day","Mid-autumn Festival","Anti-Fascist 70th Day"]:
#   print(holiday_name)
# else:
#   print('普通节假日')
 






import sys


import xlwt
import xlrd      # pip install xlrd==1.2.0
import datetime
import os


def process_kaoqin(outputPath, inputFileName):


    now = datetime.datetime.now()
    now_str = now.strftime("%Y%m%d_%H%M%S")
    write_filename = 'wtt_' + now_str + '.xls'
    write_workbook_name = outputPath + "/" + write_filename

    # 创建一个workbook设置编码
    write_workbook = xlwt.Workbook(encoding='utf-8')


    # 一次for循环一个sheet
    for processDayTwo in ["算上午下午", "一天两次即可", "两次间隔一小时", "使用另一个日期"]:

        
        # 创建一个worksheet
        write_worksheet = write_workbook.add_sheet('考勤汇总--' + processDayTwo)


        write_worksheet.write(4, 0, 'User Id')
        write_worksheet.write(4, 1, '工号')
        write_worksheet.write(4, 2, '姓名')
        write_worksheet.write(4, 3, '实际打卡次数')
        write_worksheet.write(4, 4, '考勤天数')
        write_worksheet.write(4, 5, '缺勤')
        write_worksheet.write(4, 7, "节假日打卡")

        

        # 打开Excel文件
        read_workbook = xlrd.open_workbook(inputFileName)
        all_sheets = read_workbook.sheet_names()

        newNamesRow = 6                  # 新的名字在excel的行

        allDays = 0     # 本月所有天数
        workdays = 0    # 本月工作日



        # 一个sheet，就是一个分公司的
        for sheet_name in all_sheets:
            write_worksheet.write(newNamesRow, 0, sheet_name)
            newNamesRow += 1


            namesInfos = {}
            nameToKqoQin = {}  # 名字是key，值仍是字典。该字典日期是key，然后是一个长度为2的数组记录早上下午，不想用元组，为了扩展
            


            # 获取Sheet对象
            read_sheet = read_workbook.sheet_by_name(sheet_name)

            # 获取行数和列数
            rows = read_sheet.nrows
            cols = read_sheet.ncols


            for row in range(1, rows):
                row_data = read_sheet.row_values(row)



                userId = row_data[0]
                # 目前工号和名字交换了，因为之前有的人工号不存在，本来用工号作为唯一id的，下现在用名字。
                gonghao = row_data[2]
                name = row_data[1]
                reportTimeStr = row_data[4]
                anotherDateStr = row_data[7]   #  改日期只到日，没有别的


                formatReportTime = datetime.datetime.strptime(reportTimeStr, "%Y年%m月%d日 %H:%M")
                if workdays == 0:
                    for i in range(1, 32):
                        try:
                            thisdate = datetime.date(formatReportTime.year, formatReportTime.month, i)
                            thisdateStr = thisdate.strftime("%Y-%m-%d")
                            allDays += 1
                            write_worksheet.write(4, 9 + thisdate.day, thisdateStr)
                        except(ValueError):
                            break
                        # if thisdate.weekday() < 5: # Monday == 0, Sunday == 6 
                        if is_workday(thisdate):
                            workdays += 1

                    write_worksheet.write(1, 0, '总共有{0}个sheet'.format(len(all_sheets)))
                    write_worksheet.write(2, 0, '本月是：{0}月，总共{1}天，工作日是{2}天'.format(formatReportTime.month, allDays, workdays))



                if namesInfos.get(gonghao) == None:
                    # 0记录userid， 1记录名字， 2记录日期，周末打卡次数
                    namesInfos[gonghao] = [userId, name, ""]  


                
                if processDayTwo == "使用另一个日期":
                    # 这个日期，给 "使用另一个日期" 这一类用
                    try:
                        formatAnotherDate = datetime.datetime.strptime(anotherDateStr, "%Y-%m-%d")
                    except(ValueError):
                        break
                    # 不是周末
                    # if formatAnotherDate.weekday()+1 != 6 and formatAnotherDate.weekday()+1 != 7 :
                    if is_workday(formatAnotherDate):
                        # 该工人工号不存在，先创建该字典
                        if nameToKqoQin.get(gonghao) == None:                        
                            nameToKqoQin[gonghao] = {}

                        # 该工人的该日期不存在
                        if nameToKqoQin.get(gonghao).get(anotherDateStr) == None:  
                            nameToKqoQin[gonghao][anotherDateStr] = [0, 0, []]   # 第一个代表上午，第二个代表下午，第三个代表当天打卡的时间

                        nameToKqoQin.get(gonghao).get(anotherDateStr)[0] += 1

                        
                    # 是周末，记录一下打卡日期
                    else:
                        namesInfos[gonghao][2] += "，{0}".format(anotherDateStr)

                else:
                    formatReportTimeStr = formatReportTime.strftime("%Y-%m-%d")
                    # 不是周末
                    # if formatReportTime.weekday()+1 != 6 and formatReportTime.weekday()+1 != 7:  
                    if is_workday(formatReportTime):
                        # 该工人工号不存在，先创建该字典
                        if nameToKqoQin.get(gonghao) == None:                        
                            nameToKqoQin[gonghao] = {}

                        # 该工人的该日期不存在
                        if nameToKqoQin.get(gonghao).get(formatReportTimeStr) == None:  
                            nameToKqoQin[gonghao][formatReportTimeStr] = [0, 0, []]   # 第一个代表上午，第二个代表下午，第三个代表当天打卡的时间

                        if processDayTwo == "算上午下午":
                            # 上午
                            if formatReportTime.hour < 12:
                                nameToKqoQin.get(gonghao).get(formatReportTimeStr)[0] += 1
                            # 下午
                            else:
                                nameToKqoQin.get(gonghao).get(formatReportTimeStr)[1] += 1

                        elif processDayTwo == "一天两次即可":
                            nameToKqoQin.get(gonghao).get(formatReportTimeStr)[0] += 1

                        elif processDayTwo == "两次间隔一小时":
                            reportTimes = nameToKqoQin.get(gonghao).get(formatReportTimeStr)[2] # 得到所有的打卡时间

                            if len(reportTimes) == 0:
                                nameToKqoQin.get(gonghao).get(formatReportTimeStr)[0] += 1
                            else:
                                allDaYuOneHour = True
                                for i in nameToKqoQin.get(gonghao).get(formatReportTimeStr)[2]:
                                    if (abs((formatReportTime - i).seconds) / 3600) < 1: # 时间间隔大于1小时
                                        allDaYuOneHour = False
                                        break
                                if allDaYuOneHour:
                                    nameToKqoQin.get(gonghao).get(formatReportTimeStr)[0] += 1

                            nameToKqoQin.get(gonghao).get(formatReportTimeStr)[2].append(formatReportTime)

                        
                        
                    # 是周末，记录一下打卡日期
                    else:
                        namesInfos[gonghao][2] += "，{0}".format(formatReportTime)




            userRow = newNamesRow          # 当前销售部
            # for gonghao in sorted(nameToKqoQin.keys()):
            for gonghao in nameToKqoQin.keys():
                userDict = nameToKqoQin[gonghao]

                reportCount = 0
                nowWriteColum = 9
                for date, arrs in userDict.items():
                    date = datetime.datetime.strptime(date, "%Y-%m-%d")
                    if processDayTwo == "算上午下午":
                        if arrs[0] >= 1 and arrs[1] >= 1:
                            reportCount += 2
                            write_worksheet.write(userRow, nowWriteColum + date.day, "上午下午")
                        elif arrs[0] >= 1:
                            reportCount += 1
                            write_worksheet.write(userRow, nowWriteColum + date.day, "上午")
                        elif arrs[1] >= 1:
                            reportCount += 1
                            write_worksheet.write(userRow, nowWriteColum + date.day, "下午")

                    elif (processDayTwo == "一天两次即可" or processDayTwo == "使用另一个日期") and date.month == formatReportTime.month:
                        if arrs[0] >= 2:
                            reportCount += 2
                        elif arrs[0] == 1:
                            reportCount += 1
                        if date.year >= 2024:
                            write_worksheet.write(userRow, nowWriteColum + date.day, "打卡{0}次".format(arrs[0]))
                    
                    elif processDayTwo == "两次间隔一小时":
                        if arrs[0] >= 2:
                            reportCount += 2
                        elif arrs[0] == 1:
                            reportCount += 1

                        reportTimes = sorted(arrs[2]) # 得到所有的打卡时间
                        jiangeStr = ''
                        for i in range(1, len(reportTimes)):
                            jiangeStr += "间隔{}小时\n".format(round((reportTimes[i] - reportTimes[i-1]).seconds / 3600, 1))

                        write_worksheet.write(userRow, nowWriteColum + date.day, "打卡{0}次 \n {1}".format(arrs[0], jiangeStr))

                write_worksheet.write(userRow, 0, namesInfos[gonghao][0])
                write_worksheet.write(userRow, 1, gonghao)
                write_worksheet.write(userRow, 2, namesInfos[gonghao][1])
                write_worksheet.write(userRow, 3, reportCount)
                write_worksheet.write(userRow, 4, reportCount * 1.0 / 2)
                write_worksheet.write(userRow, 5, workdays - reportCount * 1.0 / 2)

                # write_worksheet.write(userRow, 7, namesInfos[gonghao][2].split("，").length)
                write_worksheet.write(userRow, 7, namesInfos[gonghao][2])


                userRow += 1

            newNamesRow = userRow + 3


            # 存储写入的
            write_workbook.save(write_workbook_name)

    # 注意，最后需要print这个文件名字，因为java需要根据文件的输出，来判断是否正确
    print(write_filename)



# # 自己电脑处理得注释掉，放到云端需要放开。
# process_kaoqin(sys.argv[1], sys.argv[2])

# # 为了在自己电脑处理用的
if __name__ == '__main__':
    current_work_dir = os.path.abspath(os.path.dirname(__file__))           # 当前文件所在的目录，不能在命令行运行，会__file__ not defined
    process_kaoqin(current_work_dir, r'/Users/dinosaur/Downloads/aaa1.xlsx')
