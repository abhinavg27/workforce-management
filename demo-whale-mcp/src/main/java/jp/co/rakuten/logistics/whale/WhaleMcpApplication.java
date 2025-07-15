package jp.co.rakuten.logistics.whale;

import jp.co.rakuten.logistics.whale.services.ItemPickService;
import org.springframework.ai.support.ToolCallbacks;
import org.springframework.ai.tool.ToolCallback;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;

import java.util.List;

@SpringBootApplication
public class WhaleMcpApplication {

    public static void main(String[] args) {
        SpringApplication.run(WhaleMcpApplication.class, args);
    }

    @Bean
    public List<ToolCallback> itemPickTools(ItemPickService itemPickService) {
        return List.of(ToolCallbacks.from(itemPickService));
    }

}
