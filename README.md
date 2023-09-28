# BitTorent-network
A simple peer to peer bitTorent network project for my network course at university

## Introduction

This project is a BitTorrent-inspired peer-to-peer (P2P) network implementation with a central tracker. The system allows peers to share and store data directly with each other. The tracker helps peers discover the availability of files, as well as the IP addresses and ports of other peers.

## Features

- **P2P File Sharing**: Peers can share and download files from other peers in the network.

- **Tracker**: The central tracker maintains a list of available files and keeps track of which peers possess those files.

- **Direct Peer Communication**: Peers can establish direct connections to transfer data without relying solely on the tracker.

## Getting Started

### Prerequisites

- Python 3.x
- Any required Python packages (e.g., `socket`, `threading`, `bencodepy`, etc.)

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/kasra-sia/BitTorent-network.git
