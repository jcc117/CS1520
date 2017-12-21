//Jordan Carr
//Assignment 5
//Functions page

var categories;

function setup()
{
	document.getElementById("newCat").addEventListener("click", addCat, true);
	document.getElementById("newPurch").addEventListener("click", addPurch, true);
	//Check to make sure requests are supported on the browser
	var httpRequest = new XMLHttpRequest();
	
	if(!httpRequest)
	{
		alert("Uh oh, HTTP requests are not supported.");
	}
	
	update();
}

//Helper functions

//Make a general request
function makeReq(method, target, retCode, action, data)
{
	var httpRequest = new XMLHttpRequest();
	
	if(!httpRequest)
	{
		alert("Uh oh, HTTP requests are not supported.");
		return false;
	}
	
	httpRequest.onreadystatechange = makeHandler(httpRequest, retCode, action);
	httpRequest.open(method, target);
	
	if(data)
	{
		httpRequest.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
		httpRequest.send(data);
	}
	else
	{
		httpRequest.send();
	}
}

//Return a handler for a general request
function makeHandler(httpRequest, retCode, action)
{
	function handler()
	{
		if(httpRequest.readyState === XMLHttpRequest.DONE)
		{
			if(httpRequest.status === retCode)
			{
				if(httpRequest.responseText)
					console.log("recieved response text: " + JSON.parse(httpRequest.responseText));
				action(httpRequest.responseText);
			}
			else
			{
				alert("There was a problem with the request");
				console.log("Error: " + JSON.parse(httpRequest.responseText));
			}
		}
	}
	
	return handler;
}

//Clear the list of categories for updating
function clearList()
{
	document.getElementById("list").innerHTML = "";
	document.getElementById("select").innerHTML = "";
}

//Make delete functions for deleting categories below
function makeFunc(i)
{
	return function(){ delCat(i);};
}

//Clear out any user input from text bars after page update
function clearText()
{
	document.getElementById("category").value = "";
	document.getElementById("amount").value = "";
	document.getElementById("purchase").value = "";
	document.getElementById("spent").value = "";
}
//___________________________________________________________________________________________________________________________________________________________________
//Requests to the Category resource
//Add a category using a post request
function addCat()
{
	var name = document.getElementById("category").value;
	var amount = document.getElementById("amount").value;
	
	var data = "name=" + name + "&max=" + amount;
	makeReq("POST", '/cats/', 201, update, data);
}

//Delete a category using a delete request
function delCat(title)
{
	data = "name=" + title;
	makeReq("DELETE", '/cats/', 204, update, data);
}

//Update the budget list by sending a get request to get all budget information
function update(responseText)
{
	//Start with just budget names for the moment
	makeReq("GET", '/cats/', 200, repopulate);
}

//Repopulate the page
function repopulate(responseText)
{
	console.log("Repopulating");
	var cats = JSON.parse(responseText);
	cats = JSON.parse(cats);	//Account for the fact the text is 'double-stringed'
	categories = cats;	//Have the categories be stored in a global for future use
	
	var list = document.getElementById("list");
	var sel = document.getElementById("select");
	clearList(list);
	
	//Add no category option
	//Might be temporary
	var blank  = document.createElement("option");
	blank.value = "";
	sel.appendChild(blank);
	//End Temporary
	
	//Process the categories
	for(i in cats)
	{
		var item = document.createElement("li");
		var div = document.createElement("div");
		var input = document.createElement("input");
		
		//Add a delete button for the category
		input.type = "button";
		//console.log(cats[i][0]);
		input.addEventListener("click", makeFunc(cats[i]["name"]), true);
		input.value = "Delete " + cats[i]["name"];
		
		//Add the category to the dropdown menu
		var opt = document.createElement("option");
		opt.value = cats[i]["name"];
		opt.appendChild(document.createTextNode(cats[i]["name"]));
		sel.appendChild(opt);
		
		//Format the response text to a readable format for each category
		div.classList.add("category");
		div.appendChild(document.createTextNode(cats[i]["name"]));
		div.appendChild(document.createElement("br"));
		div.appendChild(document.createTextNode("Maximum Budget Amount: $" + cats[i]["max"]));
		div.appendChild(document.createElement("br"));
		div.id = cats[i]["name"];
		
		item.appendChild(div);
		div.appendChild(input);
		list.appendChild(item);
	}
	//Might be temporary
	//Add a slot for category-less items
	var noCat = document.createElement("div");
	noCat.classList.add("category");
	noCat.appendChild(document.createTextNode("No Listed Category"));
	noCat.appendChild(document.createElement("br"))
	noCat.id = "__No_Cat__";
	var listItem = document.createElement("li");
	listItem.appendChild(noCat);
	list.appendChild(listItem);
	//End Temporary
	
	//Clear out all text from user input elements
	clearText();
	
	//Make a request to get all purchases
	makeReq("GET", '/purchases/', 200, fillIn);
}
//___________________________________________________________________________________________________________________________________________________________________
//Requests to the Purchase resource
//Add a new purchase using a post request
function addPurch()
{
	var name = document.getElementById('purchase').value;
	var amount = document.getElementById('spent').value;
	var date = document.getElementById('date').value;
	var category = document.getElementById('select');
	//if(category.innerHTML != "")
	var selected = category.options[category.selectedIndex].value;
	var data = "name=" + name + "&amount=" + amount + "&date=" + date + "&category=" + selected;
	makeReq("POST", '/purchases/', 201, update, data);
}

//Fill in the categories with their purchases
function fillIn(responseText)
{
	var purch = JSON.parse(responseText);
	purch = JSON.parse(purch);	//Acount for 'double-stringed' response
	
	//Temporary for testing the get request
	var div = document.createElement("div");
	
	//Element id's in the sub array: 0 is category title, 1 is purchase name, 2 is amount, 3 is date
	for(i in purch)
	{
		//If the purchase is not in its own category, put it in the no category section
		//This is done because getElementById could potentially reference a null value
		if(purch[i]["category"] !== "")
		{
			var category = document.getElementById(purch[i]["category"]);
		}
		else	//Default, no category listed
		{
			var category = document.getElementById("__No_Cat__");
		}
		category.appendChild(document.createElement("br"));
		category.appendChild(document.createTextNode("Purchase: " + purch[i]["name"]));
		category.appendChild(document.createElement("br"));
		category.appendChild(document.createTextNode("Amount: $" + purch[i]["amount"]));
		category.appendChild(document.createElement("br"));
		category.appendChild(document.createTextNode("Date: " + purch[i]["date"]));
		category.appendChild(document.createElement("br"));
		
	}
	
	document.getElementById("list").appendChild(div);
	
	calculate(purch);
}

//Caculate the totals for each category of the budget
function calculate(purch)
{
	//Separate all purchases into their repective categories
	for(var i = 0; i < categories.length; i++)
	{
		var cat = categories[i]["name"];
		var innerList = [];
		for(var j = 0; j < purch.length; j++)
		{
			if(purch[j]["category"] == cat)
			{
				innerList.push(purch[j]);
			}
		}
		//console.log(innerList);
		
		//Process the amounts from each category
		var amounts = innerList.map(grabGrabAtt("amount"));	//Isolate the budget amounts
		if(amounts.length > 0)
		{
			var total = amounts.reduce(add);		//Calculate the total amount spent
			
			//Print the results to the page
			var div = document.getElementById(cat);
			div.appendChild(document.createElement("br"));
			div.appendChild(document.createTextNode("------------------------------------------------------------------------------------------------------"));
			div.appendChild(document.createElement("br"));
			div.appendChild(document.createTextNode("Total: $" + total));
			div.appendChild(document.createElement("br"));
			var net = categories[i]["max"] - total;		//Calculate net budget
			div.appendChild(document.createTextNode("Net Budget: $" + net));
			//Print a message if the user is over budget
			if(net < 0)
			{
				div.appendChild(document.createElement("br"));
				div.appendChild(document.createTextNode("You are over budget by $" + (total - categories[i]["max"])));
			}
		}
		else	//Default incase nothing was spent in this category
		{
			var div = document.getElementById(cat);
			div.appendChild(document.createElement("br"));
			div.appendChild(document.createTextNode("------------------------------------------------------------------------------------------------------"));
			div.appendChild(document.createElement("br"));
			div.appendChild(document.createTextNode("Net Budget: $" + categories[i]["max"]));
		}
	}
	
	//Might be temporary
	//Have a special run through of the purchases for the category-less items
	var blankList = [];
	for(var k = 0; k < purch.length; k++)
	{
		if (purch[k]["name"] == "")
		{
			blankList.push(purch[k]);
		}
	}
	
	var amounts = blankList.map(grabGrabAtt("amount"));
	if (amounts.length > 0)
	{
		var total = amounts.reduce(add);	//Calculate the total
		var div = document.getElementById("__No_Cat__");
		div.appendChild(document.createElement("br"));
		div.appendChild(document.createTextNode("------------------------------------------------------------------------------------------------------"));
		div.appendChild(document.createElement("br"));
		div.appendChild(document.createTextNode("Total: $" + total));
		div.appendChild(document.createElement("br"));	//Note, there is no net budget for category-less items
	}
	//End Temporary
}

//Grab an attribute from the returned array
function grabGrabAtt(att)
{
	function rv (item)
	{
		return item[att];
	}
	return rv;
}

//Add numbers of an array together
function add(a, b)
{
	return a + b;
}
//___________________________________________________________________________________________________________________________________________________________________
window.addEventListener("load", setup, true)