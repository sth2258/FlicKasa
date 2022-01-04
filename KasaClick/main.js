var buttonManager = require("buttons");
var http = require("http");
var url = "http://192.168.1.11:5000/";

buttonManager.on("buttonSingleOrDoubleClickOrHold", function(obj) {
	var button = buttonManager.getButton(obj.bdaddr);
	var clickType = obj.isSingleClick ? "click" : obj.isDoubleClick ? "double_click" : "hold";
	http.makeRequest({
		url: url,
		method: "POST",
		headers: {"Content-Type": "application/json"},
		content: JSON.stringify({"serial-number": button.serialNumber, "click-type": clickType}),		
	}, function(err, res) {
		console.log("request status: " + res.statusCode);
		console.log("response content: " + res.content)
	});
});

console.log("Started");