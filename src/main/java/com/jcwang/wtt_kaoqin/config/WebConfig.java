package com.jcwang.wtt_kaoqin.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.EnableWebMvc;
import org.springframework.web.servlet.config.annotation.PathMatchConfigurer;
import org.springframework.web.servlet.config.annotation.ResourceHandlerRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;
import org.springframework.web.util.UrlPathHelper;

import java.nio.charset.StandardCharsets;

@Configuration
//@EnableWebMvc
public class WebConfig implements WebMvcConfigurer {
    /**
     * 图片保存路径，自动从yml文件中获取数据
     *   示例： E:/images/
     */
    @Value("${file-save-path}")
    private String fileSavePath;

    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        /**
         * 配置资源映射
         * 意思是：如果访问的资源路径是以“/images/”开头的，
         * 就给我映射到本机的“E:/images/”这个文件夹内，去找你要的资源
         * 注意：E:/images/ 后面的 “/”一定要带上
         *
         * 说白了，就是把生成的
         * http://localhost:8080/uploadFile/2023/20230627-125705_dingdong.mp3
         * 映射到
         * file:/Users/dinosaur/jcwang/IDEA/testFolder/2023/20230627-125705_dingdong.mp3
         */
        // 配置静态资源处理
        // 注意这后面被映射的，一共要加上 "/"，不然无效
        registry.addResourceHandler("/uploadFile/**")
                .addResourceLocations("file:"+fileSavePath + "/");
    }

//    @Override
//    public void configurePathMatch(PathMatchConfigurer configurer) {
//        UrlPathHelper urlPathHelper=new UrlPathHelper();
//        urlPathHelper.setUrlDecode(false);
//        urlPathHelper.setDefaultEncoding(StandardCharsets.UTF_8.name());
//        configurer.setUrlPathHelper(urlPathHelper);
//    }

}

