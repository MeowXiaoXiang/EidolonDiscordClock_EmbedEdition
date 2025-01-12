# Eidolon Bot (Embed Edition)

## Introduction

+ 這是一個會在你的 Discord 頻道裡提供夜靈平原夜晚時鐘的機器人。
+ 此版本由小翔 [Discord：xiaoxiang_meow] 修改，介面優化為嵌入式訊息（Embed）版本，並且完全獨立於 api.warframestat.us 的資訊。
+ 此 Discord Bot 需要以下權限：
  - **Send Messages**
  - **Embed Links**
  - **Read Message History**

## Usage

### 使用 `.env` 配置
1. 將 `.env.template` 檔案重新命名為 `.env`。
2. 在 `.env` 檔案中：
   - 在 `TOKEN` 後填入你的 Discord 機器人 TOKEN。
   - 在 `ALARM_CHANNEL` 後填入要設為平原時鐘的頻道 ID（多個頻道請以逗號分隔）。

### 使用 Docker 部署
1. 確保你已經安裝了 Docker。
2. 構建映像：
   ```bash
   docker build -t eidolon-clock .
   ```
3. 運行容器：
   ```bash
   docker run -d \
       -e TOKEN=YOUR_DISCORD_BOT_TOKEN \
       -e ALARM_CHANNEL=CHANNEL_ID_1,CHANNEL_ID_2 \
       eidolon-clock
   ```
   - 你可以保留 `.env.template` 作為參考，但不需要實際使用 `.env` 檔案。

## Original Author's Project

此專案基於 [EidolonDiscordClock](https://github.com/penut85420/EidolonDiscordClock) 開發，原作者為 [penut85420](https://github.com/penut85420)。
