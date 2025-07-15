package jp.co.rakuten.logistics.whale.services;

import jakarta.annotation.PostConstruct;
import org.springframework.ai.tool.annotation.Tool;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;

@Service
public class ItemPickService {

    Map<String, Double> pickUpLocation = new HashMap<>();

    @PostConstruct
    public void init() {
        pickUpLocation = Map.of(
                "11.23", 8.0,
                "12.32", 200.0,
                "54.22", 30.0,
                "53.12", 4.0,
                "55.33", 15.0
        );
    }

    @Tool(name = "get_all_picks", description = "Get all item pick values")
    public Map<String, Double> getAllPickUpLocation() {
        return pickUpLocation;
    }

    @Tool(name = "get_picks_by_location", description = "Get item pick by location")
    public Double getPickUpLocationByLocation(String location) {
        return pickUpLocation.get(location);
    }
}
