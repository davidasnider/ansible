var config = {
	// address: "localhost",
	address: "0.0.0.0",
	port: 8080,
	ipWhitelist: ["10.9.2.1", "127.0.0.1", "::ffff:127.0.0.1", "::1"],
	useHttps: false,
	httpsPrivateKey: "",
	httpsCertificate: "",
	language: "en",
	timeFormat: 12,
	units: "imperial",
	zoom: 1.3,
	modules: [
		{
			module: "alert",
		},
		{
			module: "updatenotification",
			position: "top_bar"
		},
		{
			module: "clock",
			position: "top_left",
			config: {
				timezone: "America/Denver",
				showWeek: true,
				showSunTimes: true,
				showMoonTimes: true,
				lat: 40.57,
				lon: -111.79,
			}
		},
		{
			module: "calendar",
			header: "US Holidays",
			position: "top_left",
			config: {
				calendars: [
					{
						symbol: "calendar-check",
						url: "webcal://www.calendarlabs.com/ical-calendar/ics/76/US_Holidays.ics"
					}
				],
				maximumEntries: 4
			}
		},
		{
			module: 'calendar_monthly',
			position: 'top_left',
			config: {
				cssStyle: "block"
			}
		},
		{
			module: "currentweather",
			position: "top_center",
			config: {
				location: "Sandy, UT",
				locationID: "5781061",
				appid: "{{ vaulted.data.OPENWEATHER_APIKEY }}"
			}
		},
		{
			module: "weatherforecast",
			position: "top_center",
			header: "Weather Forecast",
			config: {
				location: "Sandy, UT",
				locationID: "5781061",
				appid: "{{ vaulted.data.OPENWEATHER_APIKEY }}"
			}
		},
		{
			module: "newsfeed",
			position: "top_bar",
			config: {
				feeds: [
					{
						title: "New York Times",
						url: "http://www.nytimes.com/services/xml/rss/nyt/HomePage.xml"
					},
				],
				updateInterval: 10000 * 60,
				showSourceTitle: true,
				showPublishDate: true,
				broadcastNewsFeeds: true,
				broadcastNewsUpdates: true
			}
		},
		{
			module: "MMM-GoogleSheets",
			header: "Weight Tracker",
			position: "top_right",
			config: {
				url: "{{vaulted.data.WEIGHT_TRACKER_URL}}",
				sheet: "Summary",
				range: "A1:E4",
				customStyles: ["background-color: transparent"]
			}
		},
		{
			module: "MMM-Wallpaper",
			position: "fullscreen_below",
			config: { // See "Configuration options" for more information.
				source: [
					"bing",
					"chromecast",
					"firetv",
				],
				slideInterval: 600 * 10000 // Change slides every minute
			}
		},
		{
			module: "MMM-Ring",
			position: "middle_center",
			config: {
				ring2faRefreshToken: "{{vaulted.data.ring2faRefreshToken}}"
			}
		},
	]
};

/*************** DO NOT EDIT THE LINE BELOW ***************/
if (typeof module !== "undefined") { module.exports = config; }