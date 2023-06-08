#include <ArduinoJson.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <time.h>
#include <Esp.h>

//###########################################< USER CONFIGURATION >###########################################//
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const char* apiKey = "YOUR_PFLANZENGLUECK_API_KEY";
const char* serverEndpoint = "https://YOUR_PFLANZENGLUECK_INSTANCE";
//#########################################< USER CONFIGURATION END >#########################################//
const char* ntpServer = "pool.ntp.org";

#define ARRAY_SIZE 100
#define MAX_DEEP_SLEEP_TIME_SECONDS 300
#define uS_TO_S_FACTOR 1000000

RTC_DATA_ATTR int32_t timestampsArray[ARRAY_SIZE];
RTC_DATA_ATTR uint8_t pinsArray[ARRAY_SIZE];
RTC_DATA_ATTR uint8_t commandsArray[ARRAY_SIZE];
RTC_DATA_ATTR bool pinsState[40] = {false}; // Assume max 40 GPIO, set all to LOW initially
RTC_DATA_ATTR uint8_t maxIndex = 0;
RTC_DATA_ATTR uint8_t currentIndex = 0;
RTC_DATA_ATTR bool just_started = true;

void ESP_go_to_deep_sleep(uint32_t seconds){
  Serial.flush();
  esp_sleep_enable_timer_wakeup(seconds*uS_TO_S_FACTOR);
  esp_deep_sleep_start();
}

void ESP_go_to_light_sleep(uint32_t seconds) {
  Serial.println("Going to Light Sleep...");
  esp_sleep_enable_timer_wakeup(seconds * uS_TO_S_FACTOR);
  esp_light_sleep_start();
}

int parsePrecalcAPIJson(Stream& stream, int32_t *timestampsArray, uint8_t *pinsArray, uint8_t *commandsArray, uint8_t *maxIndex) {
  DynamicJsonDocument doc(3*JSON_ARRAY_SIZE(ARRAY_SIZE)+JSON_OBJECT_SIZE(3)+64);
  DeserializationError error = deserializeJson(doc, stream);

  if (error) {
    Serial.print("deserializeJson() failed: ");
    Serial.println(error.c_str());
    return 1;
  }

  JsonArray timestamps = doc["timestamps"];
  JsonArray pins = doc["pins"];
  JsonArray commands = doc["commands"];

  *maxIndex = timestamps.size();

  for (uint8_t i = 0; i < *maxIndex; i++) {
    timestampsArray[i] = timestamps[i];
    pinsArray[i] = pins[i];
    commandsArray[i] = commands[i];
  }
  return 0;
}

int getPrecalcAPIInstructions(int32_t *timestampsArray, uint8_t *pinsArray, uint8_t *commandsArray, uint8_t *maxIndex){
  if ((WiFi.status() == WL_CONNECTED)) {
    HTTPClient http;
    String requestUrl = String(serverEndpoint) + "/api_precalc" + "?api_key=" + String(apiKey) + "&array_size=" + String(ARRAY_SIZE);
    Serial.println(requestUrl);
    http.begin(requestUrl);
    int httpResponseCode = http.GET();
    Serial.println(httpResponseCode);

    if (httpResponseCode > 0) {
      Stream& stream = http.getStream();
      if (parsePrecalcAPIJson(stream, timestampsArray, pinsArray, commandsArray, maxIndex)>0){
        return 1;
      }
    } else {
        Serial.print("Error code: ");
        Serial.println(httpResponseCode);
        return 2;
    }

    http.end();
  } else {
    Serial.println("WiFi Disconnected");
    return 3;
  }
    return 0;
}

int rulesChanged() {
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        String requestUrl = String(serverEndpoint) + "/api_ruleschanged" + "?api_key=" + String(apiKey);
        Serial.println(requestUrl);
        http.begin(requestUrl);
        int httpResponseCode = http.GET();
        Serial.println(httpResponseCode);

        if (httpResponseCode > 0) {
            String payload = http.getString();
            http.end();
            return payload.toInt();
        } else {
            Serial.print("Error code: ");
            Serial.println(httpResponseCode);
            http.end();
            return -1;
        }
    } else {
        Serial.println("WiFi Disconnected");
        return -1;
    }
}


void setup() {
    // Init Wifi and RTC
    Serial.begin(115200);
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
      delay(1000);
      Serial.println("Connecting to WiFi...");
    }
    Serial.println("Connected to WiFi");
    configTime(0, 0, ntpServer);
    time_t now;
    while (now < 1681330966){ // Timestamp plausibility check
      Serial.println("Initializing Clock...");
      delay(1000);
      time(&now);
    }
    Serial.println("Clock initialized");

    // Need to download new instructions?
    if (currentIndex == maxIndex || rulesChanged() == 1){
      Serial.println("Retrieving new Instructions...");
      if(getPrecalcAPIInstructions(timestampsArray, pinsArray, commandsArray, &maxIndex)>0){
        Serial.println("Error, rebooting...");
        ESP.restart();
      }
      Serial.println("Instructions successfully parsed");
      currentIndex = 0;
    }
    
    // Actions immediately pending?
    while (timestampsArray[currentIndex] <= now){
      Serial.print("Action: ");
      Serial.print(timestampsArray[currentIndex]);
      Serial.print(" - setting pin ");
      Serial.print(pinsArray[currentIndex]);
      Serial.print(" to ");
      Serial.println(commandsArray[currentIndex]);
      Serial.flush();
      pinMode(pinsArray[currentIndex], OUTPUT);
      if(commandsArray[currentIndex]){
        digitalWrite(pinsArray[currentIndex], HIGH);
      }
      else{
        digitalWrite(pinsArray[currentIndex], LOW);
      }
      pinsState[pinsArray[currentIndex]] = commandsArray[currentIndex];
      currentIndex ++;
      if (currentIndex == maxIndex){
        // Last Instruction? "Soft reboot" (by sleeping for a second) to gracefully retrieve new Instructions
        Serial.println("Last instruction processed. Rebooting...");
        ESP_go_to_deep_sleep(1);
      }
    }
    Serial.println("No more pending Actions");
    Serial.print(maxIndex-currentIndex);
    Serial.println(" Actions left in Cache");
    Serial.flush();
    if (just_started){
      // First time? Only sleep for one second. Avoids weird issues with messages not being shown 
      just_started = false;
      ESP_go_to_deep_sleep(1);
    }

    // No pending actions in the next few minutes? Go to sleep for the maximum allowed time
    // Decide on sleep mode based on pin states
    bool anyPinHigh = false;
    for (int i = 0; i < 40; i++) { // Assuming 40 is the number of GPIO pins
        if (pinsState[i]) {
            anyPinHigh = true;
            break;
        }
    }

    if (anyPinHigh) {
        // If at least one pin is HIGH, use light sleep
        Serial.println("At least one pin is HIGH. Using Light Sleep.");
        if (timestampsArray[currentIndex] - MAX_DEEP_SLEEP_TIME_SECONDS > now) {
            Serial.print("Light Sleep for ");
            Serial.print(MAX_DEEP_SLEEP_TIME_SECONDS);
            Serial.println(" seconds.");
            ESP_go_to_light_sleep(MAX_DEEP_SLEEP_TIME_SECONDS);
        } else {
            Serial.print("Light Sleep for ");
            Serial.print(timestampsArray[currentIndex] - now);
            Serial.println(" seconds.");
            ESP_go_to_light_sleep(timestampsArray[currentIndex] - now);
        }
        // Restart ESP32 after waking up from light sleep to re-run setup()
        esp_restart();
    } else {
        // If all pins are LOW, use deep sleep
        Serial.println("All pins are LOW. Using Deep Sleep.");
        if (timestampsArray[currentIndex] - MAX_DEEP_SLEEP_TIME_SECONDS > now) {
            Serial.print("Deep Sleep for ");
            Serial.print(MAX_DEEP_SLEEP_TIME_SECONDS);
            Serial.println(" seconds.");
            ESP_go_to_deep_sleep(MAX_DEEP_SLEEP_TIME_SECONDS);
        } else {
            Serial.print("Deep Sleep for ");
            Serial.print(timestampsArray[currentIndex] - now);
            Serial.println(" seconds.");
            ESP_go_to_deep_sleep(timestampsArray[currentIndex] - now);
        }
    }
}

void loop() {
  
}
