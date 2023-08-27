package com.jcwang.wtt_kaoqin.controller;

// https://blog.csdn.net/m0_59092234/article/details/126041386

// 给wtt做的考勤

// 在mac上测试和在linux上使用需要更改两个地方，第一个，python这个command；第二个，application.yml中的file-save-path这个路径。

// 需要把python文件上传到：scp /Users/dinosaur/jcwang/IDEA/WTT_kaoqin/wtt_kaoqin_python/wtt_gongzuobiao.py ubuntu@43.142.73.10:/home/ubuntu/wtt_kaoqin
// 需要把这个java包上传到：scp /Users/dinosaur/jcwang/IDEA/WTT_kaoqin/target/WTT_kaoqin-0.0.1-SNAPSHOT.jar ubuntu@43.142.73.10:/home/ubuntu/wtt_kaoqin

// 然后运行jar包：nohup java -jar /home/ubuntu/wtt_kaoqin/WTT_kaoqin-0.0.1-SNAPSHOT.jar >/home/ubuntu/wtt_kaoqin/temp_log.txt &

// 注意，这个是23/08/21前的老版本

import jakarta.servlet.http.HttpServletRequest;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import java.io.*;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;
import java.util.stream.Collectors;

/**
 * @author dinosaur
 */
@RestController
public class FileUploadController {
    @Value("${file-save-path}")
    private String fileSavePath;
    SimpleDateFormat sdf = new SimpleDateFormat("yyyy/");
    SimpleDateFormat sdf2 = new SimpleDateFormat("yyyyMMdd-HHmmss_");

    @PostMapping("/upload")
    public String upload(MultipartFile uploadFile, HttpServletRequest req) {
//        String realPath =
//                req.getSession().getServletContext().getRealPath("/uploadFile/");
//        String format = sdf.format(new Date());
//        File folder = new File(realPath + format);



        String visit_origin_filePath = "";
        String visit_output_filePath = "";
        String real_filePath = "";
        String format = sdf.format(new Date());
        File folder = new File(fileSavePath + format);
        if (!folder.isDirectory()) {
            folder.mkdirs();
        }

        String oldName = uploadFile.getOriginalFilename();
//        String newName = UUID.randomUUID().toString() +
//                oldName.substring(oldName.lastIndexOf("."), oldName.length());
        String newName = sdf2.format(new Date()) + oldName;

        try {
            uploadFile.transferTo(new File(folder, newName));
            real_filePath = folder + "/" + newName;

            // 这个是我上传的文件。
            visit_origin_filePath = req.getScheme() + "://" + req.getServerName() + ":" +
                    req.getServerPort() + "/uploadFile/" + format + newName;

            // 下面这个是python输出的文件，webconfig里面首先截取吧uploadFile去掉的。
            String result = executePython(real_filePath);
            if (result.endsWith(".xls")) {
                visit_output_filePath = "wtt，请访问下列地址获取文件：" + req.getScheme() + "://" + req.getServerName() + ":" +
                        req.getServerPort() + "/uploadFile/output/" + result;
            } else {
                visit_output_filePath = "有错误，请联系wjc。";
            }

        } catch (IOException e) {
            e.printStackTrace();
            return "上传失败! ";
        }
        return visit_output_filePath;
    }

    public static List<String> readProcessOutput(InputStream inputStream) throws IOException {
        try (BufferedReader output = new BufferedReader(new InputStreamReader(inputStream))) {
            return output.lines()
                    .collect(Collectors.toList());
        }
    }

    public String executePython(String inputFileName) {
        try {
            File outputFilePath = new File( fileSavePath + "/output");
            if (!outputFilePath.isDirectory()) {
                outputFilePath.mkdirs();
            }

            // /Users/dinosaur/jcwang/IDEA/testFolder/wtt_gongzuobiao.py
            // 后面三个参数，第一个是python文件路径，第二个是输出路径文件夹，第三个是输入的excel文件。
            String pythonFileName = fileSavePath + "wtt_gongzuobiao.py";

            ProcessBuilder processBuilder = new ProcessBuilder("python", pythonFileName, fileSavePath + "/output", inputFileName);
//            ProcessBuilder processBuilder = new ProcessBuilder("/Users/dinosaur/jcwang/pythonvenv/venvpaper39/bin/python", pythonFileName, fileSavePath + "/output", inputFileName);
            //切换到工作目录
            // processBuilder.directory(new File(fileSavePath));
            processBuilder.redirectErrorStream(true);

            Process process = processBuilder.start();
            List<String> results = readProcessOutput(process.getInputStream());
            System.out.println("results = " + results);

            // 等待进程完成
            int exitCode = process.waitFor();
            System.out.println("Exited with error code " + exitCode);

            // 返回输出的文件名字
            return results.get(0);
        } catch (Exception e) {
            e.printStackTrace();
        }

        return "失败了";
    }
}


