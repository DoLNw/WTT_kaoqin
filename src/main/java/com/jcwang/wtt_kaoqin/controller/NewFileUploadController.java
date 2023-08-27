package com.jcwang.wtt_kaoqin.controller;

import jakarta.servlet.http.HttpServletRequest;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.servlet.ModelAndView;

import java.io.*;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;
import java.util.stream.Collectors;


// https://blog.csdn.net/m0_59092234/article/details/126041386

// 给wtt做的考勤

// 在mac上测试和在linux上使用需要更改两个地方，第一个，python这个command；第二个，application.yml中的file-save-path这个路径。

// 需要把python文件上传到：scp /Users/dinosaur/jcwang/IDEA/WTT_kaoqin/wtt_kaoqin_python/wtt_gongzuobiao.py ubuntu@43.142.73.10:/home/ubuntu/wtt_kaoqin
// 需要把这个java包上传到：scp /Users/dinosaur/jcwang/IDEA/WTT_kaoqin/target/WTT_kaoqin-0.0.1-SNAPSHOT.jar ubuntu@43.142.73.10:/home/ubuntu/wtt_kaoqin

// 然后运行jar包：nohup java -jar /home/ubuntu/wtt_kaoqin/WTT_kaoqin-0.0.1-SNAPSHOT.jar >/home/ubuntu/wtt_kaoqin/temp_log.txt &
// 查看日志： cat /home/ubuntu/wtt_kaoqin/temp_log.txt

// ps -ef | grep java


// 注意，这个是23/08/21后的新版本


/**
 * @author dinosaur
 */
@Controller
public class NewFileUploadController {
    @Value("${file-save-path}")
    private String fileSavePath;
    SimpleDateFormat sdf = new SimpleDateFormat("yyyy/");
    SimpleDateFormat sdf2 = new SimpleDateFormat("yyyyMMdd-HHmmss_");



    @GetMapping("/upload/{pythonFileName}")
    public ModelAndView upload(ModelAndView modelAndView, @PathVariable("pythonFileName") String pythonFileName) {

        modelAndView.addObject("pythonFileName", pythonFileName);

        modelAndView.setViewName("upload");

        return modelAndView;
    }





    @ResponseBody
    @RequestMapping("/uploadAndGet/{pythonFileName}")
    public String upload(MultipartFile uploadFile, HttpServletRequest req, @PathVariable("pythonFileName") String pythonFileName) {
        String visitOriginFilePath = "";
        String visitOutputFilePath = "";
        String realFilePath = "";
        String format = sdf.format(new Date());
        // 上传后文件的存储位置
        File folder = new File(fileSavePath + "/" + format);
        if (!folder.isDirectory()) {
            boolean mkdirs = folder.mkdirs();
        }

        try {
            String oldName = uploadFile.getOriginalFilename();
            String newName = sdf2.format(new Date()) + oldName;
            // 将上传的文件转到下面这个目录
            uploadFile.transferTo(new File(folder, newName));
            // 所以真正的输入文件地址是这个
            realFilePath = folder + "/" + newName;

            // 这个是我上传的文件地址，没有被处理的。外面可以访问的??
            visitOriginFilePath = req.getScheme() + "://" + req.getServerName() + ":" +
                    req.getServerPort() + "/uploadFile/" + format + newName;

            try {
                // 下面这个是python输出的文件，webconfig里面首先截取吧uploadFile去掉的。
                String result = executePython(realFilePath, pythonFileName);
                if (result.endsWith(".xls")) {
                    visitOutputFilePath = "破事儿一堆的wtt，请访问下列地址获取文件：" + req.getScheme() + "://" + req.getServerName() + ":" +
                            req.getServerPort() + "/uploadFile/output/" + result;
                } else {
                    visitOutputFilePath = "执行python有错误，请联系wjc。错误信息是：python的返回信息不对，不成功。\n\n返回信息时" + result;
                }
            } catch (Exception e) {
                e.printStackTrace();
                visitOutputFilePath = "执行python有错误，请联系wjc。错误信息是：\n\n" + e.getLocalizedMessage();
            }


        } catch (IOException e) {
            e.printStackTrace();
            return "上传失败! 错误信息是：\n" + e.getLocalizedMessage();
        }

        return visitOutputFilePath;
    }

    public static List<String> readProcessOutput(InputStream inputStream) throws IOException {
        try (BufferedReader output = new BufferedReader(new InputStreamReader(inputStream))) {
            return output.lines()
                    .collect(Collectors.toList());
        }
    }

    public String executePython(String inputFileName, String pythonFileName) throws IOException, InterruptedException {
        File outputFilePath = new File( fileSavePath + "/output");
        if (!outputFilePath.isDirectory()) {
            boolean mkdirs = outputFilePath.mkdirs();
        }

        // /Users/dinosaur/jcwang/IDEA/testFolder/wtt_gongzuobiao.py
        // 后面三个参数，第一个是python文件路径，第二个是输出路径文件夹，第三个是输入的excel文件。
        String pythonFileNameLoca = fileSavePath + "/" + pythonFileName +  ".py";

        ProcessBuilder processBuilder = new ProcessBuilder("python", pythonFileNameLoca, outputFilePath.toString(), inputFileName);
//        System.out.println(pythonFileNameLoca);
//        ProcessBuilder processBuilder = new ProcessBuilder("/Users/dinosaur/jcwang/pythonvenv/venvpaper39/bin/python", pythonFileNameLoca, fileSavePath + "/output", inputFileName);
        //切换到工作目录
        // processBuilder.directory(new File(fileSavePath));
        processBuilder.redirectErrorStream(true);

        Process process = processBuilder.start();
        List<String> results = readProcessOutput(process.getInputStream());
        System.out.println("results = " + results);

        // 等待进程完成
        int exitCode = process.waitFor();
        System.out.println("Exited with status code: " + exitCode);

        // 返回输出的文件名字
        return results.get(0);

    }
}



