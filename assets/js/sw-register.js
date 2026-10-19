if(location.protocol.indexOf("http")===0&&"serviceWorker"in navigator){window.addEventListener("load",function(){navigator.serviceWorker.register("sw.js");});}
