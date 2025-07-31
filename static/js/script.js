let version = "";
let lastUpdated = "";

//make async request to pypi json endpoint to get the software's current version
async function loadVersion() {
    try {
        const response = await fetch("https://pypi.org/pypi/iso3166-2/json");
        if (!response.ok) throw new Error("Failed to fetch version");
        const data = await response.json();
        version = data.info.version;
        console.log("Version: ", version);
        // const versionElem = document.getElementById("version");
        // if (versionElem) {
        //     versionElem.innerHTML = "<b>Version: </b>" + version;
        // }
    } catch (error) {
        console.error("Error fetching version:", error);
    }
}

//make async request to pypi json endpoint to get the software's latest month update
async function loadLatestUpdate() {
    try {
        const response = await fetch("https://pypi.org/pypi/iso3166-2/json");
        if (!response.ok) throw new Error("Failed to fetch version metadata");
        const data = await response.json();

        const latestVersion = data.info.version;
        const releaseFiles = data.releases[latestVersion];
        
        if (!releaseFiles || releaseFiles.length === 0) {
            throw new Error("No release files found for the latest version");
        }

        const uploadTime = releaseFiles[0].upload_time_iso_8601 || releaseFiles[0].upload_time;
        const uploadDate = new Date(uploadTime);

        // lastUpdated = (uploadDate.getUTCMonth() + 1) + uploadDate.getUTCFullYear()
        lastUpdated = new Intl.DateTimeFormat("en-US", {
            year: "numeric",
            month: "long"
        }).format(uploadDate);

        console.log("Last Updated: ", lastUpdated);
        
    } catch (error) {
        console.error("Error fetching update date:", error);
    }
}

window.onload = async function(){ 

    //pull iso3166-2 version from pypi
    await loadVersion();

    //pull iso3166-2 latest month and year from pypi
    await loadLatestUpdate();

    //set version to its element after page load
    document.getElementById("version").innerHTML = "<b>Version: </b>" + version;

    //set latest update month to its element after page load
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
    function calcElements () {
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
    calcElements();

    //on page load, call create elements function 
    window.onload = () => { 
        calcElements();
    };

    //create resize event listener, used when page is resized
    window.addEventListener("resize", debounce(function (e) {
        e.preventDefault();
        calcElements();
    }));

    //create scroll event listener, used to scroll between sections on page
    window.addEventListener('scroll', function (e) {
        e.preventDefault();
        onScroll();
    });

    //query all buttons that start with ID "copy-text-btn"
    const copyButtons = document.querySelectorAll('[id^="copy-text-btn"]');

    //iterate over all copy to clipboard buttons and create event listener that copies the API URL once clicked & displays tooltip
    copyButtons.forEach(button => {
        button.addEventListener("click", () => {
            const apiURL = button.getAttribute('data-api-url');
            navigator.clipboard.writeText(apiURL).then(() => {
                console.log('API URL copied to clipboard: ' + apiURL);

                // Show tooltip
                const tooltip = button.querySelector('.tooltip-text');
                if (tooltip) {
                    tooltip.style.visibility = 'visible';
                    tooltip.style.opacity = '1';

                    setTimeout(() => {
                        tooltip.style.visibility = 'hidden';
                        tooltip.style.opacity = '0';
                    }, 1500); // hide after 1.5 seconds
                }
            });
        });
    });

}