package com.mcp.server.controller;

import com.mcp.server.model.Player;
import com.mcp.server.service.PlayerService;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/players")
public class PlayerController {
  private final PlayerService playerService;

  public PlayerController(PlayerService playerService) {
    this.playerService = playerService;
  }

  @GetMapping
  public List<Player> getAllPlayers() {
    return playerService.getAllPlayers();
  }

  @GetMapping("/{username}")
  public Player getPlayerByUsername(@PathVariable String username) {
    return playerService.getPlayerByUsername(username);
  }

  @PostMapping
  public Player savePlayer(@RequestBody Player player) {
    return playerService.savePlayer(player);
  }
}