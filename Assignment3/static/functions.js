//Jordan Carr
//proj3

var timeoutID;
var timeout = 1000;
var highest_known_msg = 0;

//Set up the page
function setup()
{
	document.getElementById("submit").addEventListener("click", addMsg, true);
	timeoutID = window.setTimeout(poller, timeout);
}

function poller()
{
	var httpRequest = new XMLHttpRequest();
	if(!httpRequest)
	{
		alert("Requests not supported");
		return false;
	}
	
	//Check that the chatroom still exists
	httpRequest.onreadystatechange = function(){ handleExist(httpRequest)};
	httpRequest.open("GET", "/check_chat/");
	httpRequest.send();
	
	//Get the latest messages
	httpRequest2 = new XMLHttpRequest();
	httpRequest2.onreadystatechange = function(){ handlePoll(httpRequest2)};
	httpRequest2.open("POST", "/get_messages/");
	httpRequest2.setRequestHeader('Content-Type', 'application/json');
	httpRequest2.send(highest_known_msg);
	
	//Get the latest message id
	httpRequest3 = new XMLHttpRequest();
	httpRequest3.onreadystatechange = function(){ handleID(httpRequest3)};
	httpRequest3.open("GET", "/get_latest_id/");
	httpRequest3.send();
		
}

function handlePoll(httpRequest)
{
	if(httpRequest.readyState === XMLHttpRequest.DONE)
	{
		if(httpRequest.status === 200)
		{
			//Add the values to the table
			var table = document.getElementById("theTable");
			var rows = JSON.parse(httpRequest.responseText);
			for(var i = 0; i < rows.length; i++)
			{
				addRow(rows[i]);
			}
			
			timeoutID = window.setTimeout(poller, timeout);
		}
		else
		{
			//alert("There was a problem with the poll request");
		}
	}
}
//Handle checking for the chatroom existence
function handleExist(httpRequest)
{
	if(httpRequest.readyState === XMLHttpRequest.DONE)
	{
		if(httpRequest.status === 200)
		{
			var exist = JSON.parse(httpRequest.responseText);
			if(exist != 1)
			{
				alert("This chatroom does not exist anymore. Redirecting to your chatroom list.");
				window.history.pushState("Chatroom does not exist", "InstaChat", "/");
				location.reload();
			}
		}
		else
		{
			alert("There was a problem with the check request");
		}
	}
}
//Handle getting the latest ID
function handleID(httpRequest)
{
	if(httpRequest.readyState === XMLHttpRequest.DONE)
	{
		if(httpRequest.status === 200)
		{
			highest_known_msg = JSON.parse(httpRequest.responseText);
		}
		else
		{
			//alert("There was a problem with the ID request");
		}
	}
}
//Add a message to the chatroom
function addMsg()
{
	var httpRequest = new XMLHttpRequest();
	if(!httpRequest)
	{
		alert("Requests not supported");
		return false;
	}
	
	var msg = document.getElementById("texter").value;
	httpRequest.onreadystatechange = function(){ handleAdd(httpRequest)};
	httpRequest.open("POST", "/add_message/");
	httpRequest.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
	var data = 'texter=' + msg;
	httpRequest.send(data);
}

function handleAdd(httpRequest)
{
	if(httpRequest.readyState === XMLHttpRequest.DONE)
	{
		if(httpRequest.status === 200)
		{
			console.log("Add is all good");
			//timeoutID = window.setTimeout(poller, timeout);
		}
		else
		{
			//alert("There was a problem with the add request");
		}
	}
}

//Add a new row to the table
function addRow(row)
{
	var tableRef = document.getElementById("theTable");
	
	//Format the new message into a div and add it to the table
	newDiv = document.createElement('div');
	newDiv.classList.add("message");
	newText = document.createTextNode(row);
	newDiv.appendChild(newText);
	tableRef.appendChild(newDiv);
}

//Get the chat id
window.addEventListener("load", setup, true);