// Defines the html to be used for the sidebar pane
chrome.devtools.panels.elements.createSidebarPane(
  "Mister Crawler",
  function (sidebar) {
    sidebar.setPage("sidebar/sidebar.html");
  }
);

// onSelectionChanged: whe the user select a new element
// source: https://stackoverflow.com/questions/61108602/put-xpath-to-selected-element-in-sidebar-extension-html
// source: https://stackoverflow.com/questions/25128330/how-to-i-send-selected-element-from-devtools-page-to-chrome-sidebar-page/36841655
chrome.devtools.panels.elements.onSelectionChanged.addListener(() => {
  // the function must be declared in the same context as $0, so we need to
  // declare it like this:
  chrome.tabs.executeScript(
    {
      code: 
        `function getXpathTo(element) {
          if (element.id!=='')
              return 'id("'+element.id+'")';
          if (element===document.body)
              return element.tagName;

          var ix= 0;
          var siblings= element.parentNode.childNodes;
          for (var i= 0; i<siblings.length; i++) {
              var sibling= siblings[i];
              if (sibling===element)
                  return getXpathTo(element.parentNode)+'/'+element.tagName+'['+(ix+1)+']';
              if (sibling.nodeType===1 && sibling.tagName===element.tagName)
                  ix++;
          }
        }`
      ,
      runAt: 'document_start',
    },
    // function that receives the element selected
    () => {
      chrome.devtools.inspectedWindow.eval(
        `(${() => {
          // sends message to script inside panel
          chrome.extension.sendMessage(
            { type: "xpath", content: getXpathTo($0)},
            function (response) {}
          );
        }})()`,
        {useContentScriptContext: true}
      );
    }
  );
});

// chrome.extension.onMessage.addListener(
//   function (request, sender, sendResponse) {
//     console.log("received message type: " + request.type);
//     if(request.type == "table"){
//       console.log(">>>>>>>>>>>>>>> Received message:");
//       console.log(">>>>>>>>>>>>>>> " + request.xpath);
//       var el = getElementByXpath(request.xpath);
//       console.log(">>>>>>>>>>>>>>> " + el);

//       sendResponse({ table: JSON.stringify(el.innerHtml) });
//     }
//   }
// );

chrome.extension.onMessage.addListener(
  function (request, sender, sendResponse) {
    if(request.type == "asking_for_table"){
      chrome.tabs.executeScript(
        {
          code: 
            `
            function getElementByXpath(path) {
              console.log("getElementByXpath says Hello.......");
              return document.evaluate(path, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
            }
            function getContentByXpath(path){
              console.log("getContentByXpath says Hi.......");
              return getElementByXpath(path).innerHTML;
            }
            var path = \"${request.xpath}\";`
          ,
          runAt: 'document_start',
        },
        // function that receives the element selected
        () => {
          console.log("HERE!!!!!!!!!!!! " + request.xpath);
          chrome.devtools.inspectedWindow.eval(
            `(${() => {
              // sends message to script inside panel
              console.log("tinha q ter algo aqui >>>>> ");
              console.log(path);
              console.log(" <<<");
              chrome.extension.sendMessage(
                // { type: "sending_table", table: getContentByXpath(request.xpath) },
                { type: "sending_table", table: getContentByXpath(path) },
                function (response) { }
              );
            }})()`,
            { useContentScriptContext: true }
          );
        }
      );
      sendResponse({status: "Ok?"})    
    }
  }
);

function getElementByXpath(path) {
  return document.evaluate(path, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
}

// The 2 functions below are not actually used here, I'm just saving them. 
// To be used they need to be in tha same context of where the element is
// so they must be declared as onSelectionChanged to be used with $0

// source: https://stackoverflow.com/questions/2631820/how-do-i-ensure-saved-click-coordinates-can-be-reloaed-to-the-same-place-even-i/2631931#2631931
function getXpathTo(element) {
  if (element.id !== '')
    return 'id("' + element.id + '")';

  if (element === document.body)
    return element.tagName;

  var ix = 0;
  var siblings = element.parentNode.childNodes;
  for (var i = 0; i < siblings.length; i++) {
    var sibling = siblings[i];
    if (sibling === element)
      return getXpathTo(element.parentNode) + '/' + element.tagName + '[' + (ix + 1) + ']';
    if (sibling.nodeType === 1 && sibling.tagName === element.tagName)
      ix++;
  }
}

// source: https://stackoverflow.com/questions/3620116/get-css-path-from-dom-element
function getCssSelectorTo(el) {
  if (!(el instanceof Element)) return;
  var path = [];
  while (el.nodeType === Node.ELEMENT_NODE) {
    var selector = el.nodeName.toLowerCase();
    if (el.id) {
      selector += '#' + el.id;
    }
    else {
      var sib = el, nth = 1;
      while (sib.nodeType === Node.ELEMENT_NODE && (sib = sib.previousSibling) && nth++);
      selector += ":nth-child(" + nth + ")";
    }
    path.unshift(selector);
    el = el.parentNode;
  }
  return path.join(" > ");
}