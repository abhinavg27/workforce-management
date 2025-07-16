package com.mcp.server.service;

import com.mcp.server.model.Player;
import com.mcp.server.repository.PlayerRepository;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class PlayerService {
  private final PlayerRepository playerRepository;

  public PlayerService(PlayerRepository playerRepository) {
    this.playerRepository = playerRepository;
  }

  public List<Player> getAllPlayers() {
    return playerRepository.findAll();
  }

  public Player getPlayerByUsername(String username) {
    return playerRepository.findByUsername(username);
  }

  public Player savePlayer(Player player) {
    return playerRepository.save(player);
  }
}