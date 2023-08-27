# 服务器上面的python环境用的是本地的，没有创建虚拟环境。
# https://blog.csdn.net/m0_59092234/article/details/126041386

# 给wtt做的考勤

# 在mac上测试和在linux上使用需要更改两个地方，第一个，python这个command；第二个，application.yml中的file-save-path这个路径。

# 需要把python文件上传到：
# scp /Users/dinosaur/jcwang/IDEA/WTT_kaoqin/wtt_kaoqin_python/wtt_gongzuobiao.py ubuntu@43.142.73.10:/home/ubuntu/wtt_kaoqin

# 需要把这个java包上传到：
# scp /Users/dinosaur/jcwang/IDEA/WTT_kaoqin/target/WTT_kaoqin-0.0.1-SNAPSHOT.jar ubuntu@43.142.73.10:/home/ubuntu/wtt_kaoqin

# 然后运行jar包：nohup java -jar /home/ubuntu/wtt_kaoqin/WTT_kaoqin-0.0.1-SNAPSHOT.jar >/home/ubuntu/wtt_kaoqin/temp_log.txt &


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
    # 创建一个worksheet
    write_worksheet = write_workbook.add_sheet('汇总sheet')






    # 打开Excel文件
    read_workbook = xlrd.open_workbook(inputFileName)

    # 获取Sheet对象
    read_sheet = read_workbook.sheet_by_name('考勤汇总报表')

    # 获取行数和列数
    rows = read_sheet.nrows
    cols = read_sheet.ncols





    write_worksheet.write(1, 0, '姓名')
    write_worksheet.write(1, 1, '部门')
    write_worksheet.write(1, 2, '实际出勤天数')
    write_worksheet.write(1, 3, '工作日')
    write_worksheet.write(1, 4, '休息日')
    write_worksheet.write(1, 5, '节假日')
    write_worksheet.write(1, 6, '迟到次数')
    write_worksheet.write(1, 7, '迟到时长')
    write_worksheet.write(1, 8, '缺勤天数')
    write_worksheet.write(1, 9, '漏卡次数')
    write_worksheet.write(1, 10, '备注（旷工）')
    write_worksheet.write(1, 11, '备注（哺乳假）')

    write_worksheet.write(1, 12, '事假病假产假')
    write_worksheet.write(1, 13, '丧假婚假陪产假新冠病假')




    # 输出每行的数据
    for i in range(5,rows):
        row_data = read_sheet.row_values(i)
        # print(row_data)

        name = row_data[0]

        biaogedeyingchuqin_day = float(row_data[2])
        
        department = row_data[1]

        chidao_count = float(row_data[4])
        chidao_hour = float(row_data[5])


        # 矿工次数
        kuanggong_count = row_data[12]

        if "温州分公司" in department:
            kuanggong_day = float(row_data[13]) / 7.5
        else:
            kuanggong_day = float(row_data[13]) / 8

        louqian_count = float(row_data[14])
        tiaoxiu_hour = float(row_data[15])
        shijia_hour = float(row_data[16])
        bingjia_hour = float(row_data[17])
        chanjia_hour = float(row_data[18])
        peichanjia_hour = float(row_data[19])
        hunjia_hour = float(row_data[20])
        sangjia_hour = float(row_data[21])
        burujia_hour = float(row_data[22])
        gongshang_hour = float(row_data[23])
        xinguan_hour = float(row_data[24])

        # 缺勤=漏签+旷工+事假+病假+丧假+婚假+产假+陪产假+新冠病假，哺乳假加到出勤天数里面
        if "温州分公司" in department:
            queqin_day = (shijia_hour + bingjia_hour +sangjia_hour + hunjia_hour + chanjia_hour + peichanjia_hour + xinguan_hour) / 7.5
        else:
            queqin_day = (shijia_hour + bingjia_hour +sangjia_hour + hunjia_hour + chanjia_hour + peichanjia_hour + xinguan_hour) / 8
        queqin_day += louqian_count / 2 + kuanggong_day

        shijichuqin_day = biaogedeyingchuqin_day - queqin_day

        
        write_worksheet.write(i, 0, name)
        write_worksheet.write(i, 1, department)
        write_worksheet.write(i, 2, shijichuqin_day)

        if chidao_count != 0:
            write_worksheet.write(i, 6, chidao_count)
        if chidao_hour != 0:
            write_worksheet.write(i, 7, chidao_hour)
        if queqin_day != 0:
            write_worksheet.write(i, 8, queqin_day)
        if louqian_count != 0:
            write_worksheet.write(i, 9, louqian_count)
        if kuanggong_day != 0:
            write_worksheet.write(i, 10, "旷工{}天".format(kuanggong_day))
        if burujia_hour != 0:
            write_worksheet.write(i, 11, "哺乳假{}h".format(burujia_hour))


        shibingchanbeizhu = ""
        if shijia_hour != 0:
            shibingchanbeizhu += "事假{}h，".format(shijia_hour)
        if bingjia_hour != 0:
            shibingchanbeizhu += "病假{}h，".format(bingjia_hour)
        if chanjia_hour != 0:
            shibingchanbeizhu += "产假{}h，".format(chanjia_hour)
        write_worksheet.write(i, 12, shibingchanbeizhu)

        sanghunpeichanxinguanbeizhu = ""
        if gongshang_hour != 0:
            sanghunpeichanxinguanbeizhu += "丧假{}h，".format(gongshang_hour)
        if hunjia_hour != 0:
            sanghunpeichanxinguanbeizhu += "婚假{}h，".format(hunjia_hour)
        if peichanjia_hour != 0:
            sanghunpeichanxinguanbeizhu += "陪产假{}h，".format(peichanjia_hour)
        if xinguan_hour != 0:
            sanghunpeichanxinguanbeizhu += "新冠病假假{}h，".format(xinguan_hour)
        write_worksheet.write(i, 13, sanghunpeichanxinguanbeizhu)


        print(write_filename)


        print('{}，姓名：{}，实际出勤天数：{}，迟到次数：{}，迟到时长：{}，矿工次数：{}，矿工天：{}，缺勤：{}，陪产：{}'.format(i, name, shijichuqin_day, chidao_count, chidao_hour, kuanggong_count, kuanggong_day, queqin_day,peichanjia_hour))


        # return write_filename


    # 存储写入的
    write_workbook.save(write_workbook_name)

# 自己电脑处理得注释掉，放到云端需要放开。
process_kaoqin(sys.argv[1], sys.argv[2])

# # 为了在自己电脑处理用的
# if __name__ == '__main__':
#     current_work_dir = os.path.abspath(os.path.dirname(__file__))           # 当前文件所在的目录，不能在命令行运行，会__file__ not defined
#     process_kaoqin(current_work_dir, r'/Users/dinosaur/jcwang/IDEA/WTT_kaoqin/wtt_kaoqin_python/2023年5月分公司考勤.xlsx')
