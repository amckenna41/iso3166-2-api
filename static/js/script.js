let version = "";
let lastUpdated = "";
let timestamp = "";
var monthNames = ["January","February","March","April","May","June","July","August","September","October","November","December"];

//make get request to pypi json endpoint
fetch("https://pypi.org/pypi/iso3166-2/json")
    .then(response => { 
    if (!response.ok) { 
        throw new Error("Error making GET request to PyPI server"); 
    } 
    return response.json();
    })
    .then(data => { 
        //parse version from pypi object
        version = data['info']['version']

        //timestamp for latest published release of software on pypi
        timestamp = new Date (String(data['releases'][version][0]['upload_time']) + "Z")
        
        //extract month and year from software release timestamp
        lastUpdated = monthNames[timestamp.getMonth()] + " " + timestamp.getFullYear()
    })
    .catch(error => { 
        console.error("Error making GET request to PyPI server: ", error);});

window.onload = function(){ 

    //delay for author element to allow for Version and Last Updated metadata to be pulled from pypi first
    setTimeout(function(){
        document.getElementById('author').style.visibility = "visible";
        },30);

    //set version to its element after page load
    document.getElementById("version").innerHTML = "<b>Version: </b>" + version;
    document.getElementById("last-updated").innerHTML = "<b>Last Updated: </b>" + lastUpdated;

    //iterate over each menu section element, highlight it and scroll to it on page when hovered over & clicked
    [].forEach.call(document.querySelectorAll('.scroll-to-link'), function (div) {
        div.onclick = function (e) {
            e.preventDefault();
            //get target element id
            var target = this.dataset.target;
            //scroll to current active element
            document.getElementById(target).scrollIntoView({ behavior: 'smooth' });
            //get all menu section elements
            var elems = document.querySelectorAll(".content-menu ul li");
            //iterate over the other elements and set them to inactive
            [].forEach.call(elems, function (el) {
                el.classList.remove("active");
            });
            //current active menu section on page
            this.classList.add("active");
            return false;
        };
    });
    
    //create event listener that toggles if button menu is clicked
    document.getElementById('button-menu-mobile').onclick = function (e) {
        e.preventDefault();
        document.querySelector('html').classList.toggle('menu-opened');
    }

    //create event listener that toggles if left menu section is clicked/closed
    document.querySelector('.left-menu .mobile-menu-closer').onclick = function (e) {
        e.preventDefault();
        document.querySelector('html').classList.remove('menu-opened');
    }

    //set resize timer 
    function debounce (func) {
        var timer;
        return function (event) {
            if (timer) clearTimeout(timer);
            timer = setTimeout(func, 100, event);
        };
    }

    var elements = [];

    //get dimensions of each menu div section on main content page
    function calculElements () {
        var totalHeight = 0; //total height for div 
        elements = [];
        [].forEach.call(document.querySelectorAll('.content-section'), function (div) {
            var section = {};
            section.id = div.id;
            totalHeight += div.offsetHeight;
            section.maxHeight = totalHeight - 25;
            elements.push(section);
        });
        //call update scroll function 
        onScroll();
    }

    //keep track and update the scroll height and highlight active section at centre of page from left menu
    function onScroll () {
        var scroll = window.pageYOffset;
        for (var i = 0; i < elements.length; i++) {
            var section = elements[i];
            if (scroll <= section.maxHeight) {
                var elems = document.querySelectorAll(".content-menu ul li");
                [].forEach.call(elems, function (el) {
                    el.classList.remove("active");
                });
                var activeElems = document.querySelectorAll(".content-menu ul li[data-target='" + section.id + "']");
                [].forEach.call(activeElems, function (el) {
                    el.classList.add("active");
                });
                break;
            }
        }

        //get the last element of body at bottom of page/end of scroll
        if (window.innerHeight + scroll + 5 >= document.body.scrollHeight) { // end of scroll, last element
            var elems = document.querySelectorAll(".content-menu ul li");
            [].forEach.call(elems, function (el) {
                el.classList.remove("active");
            });
            var activeElems = document.querySelectorAll(".content-menu ul li:last-child");
            [].forEach.call(activeElems, function (el) {
                el.classList.add("active");
            });
        }
    }

    //call create elements function
    calculElements();

    //on page load, call create elements function 
    window.onload = () => { 
        calculElements();
    };

    //create resize event listener, used when page is resized
    window.addEventListener("resize", debounce(function (e) {
        e.preventDefault();
        calculElements();
    }));

    //create scroll event listener, used to scroll between sections on page
    window.addEventListener('scroll', function (e) {
        e.preventDefault();
        onScroll();
    });
    
    //iterate over all copy to clipboard buttons and create event listener that copies the API URL once clicked
    let copyTextBtn1 = document.querySelector("#copy-text-btn1");
    let copyTextBtn2 = document.querySelector("#copy-text-btn2");
    let copyTextBtn3 = document.querySelector("#copy-text-btn3");

    copyTextBtn1.addEventListener("click", function () {
        let apiURL = copyTextBtn1.getAttribute('data-api-url')
        navigator.clipboard.writeText(apiURL);
        console.log('API URL copied to clipboard: ' + apiURL);
    });

    copyTextBtn2.addEventListener("click", function () {
        let apiURL = copyTextBtn2.getAttribute('data-api-url')
        navigator.clipboard.writeText(apiURL);
        console.log('API URL copied to clipboard: ' + apiURL);
    });

    copyTextBtn3.addEventListener("click", function () {
        let apiURL = copyTextBtn3.getAttribute('data-api-url')
        navigator.clipboard.writeText(apiURL);
        console.log('API URL copied to clipboard: ' + apiURL);
    });
}