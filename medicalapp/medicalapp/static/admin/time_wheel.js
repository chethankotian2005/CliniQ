// Simple time wheel for inputs with class 'timewheel'
// This is a lightweight roller: clicking the input opens a small wheel UI to pick hours/minutes

document.addEventListener('click', function(e) {
    // Close any open wheels when clicking outside
    if (!e.target.closest('.time-wheel-container') && !e.target.classList.contains('timewheel')) {
        document.querySelectorAll('.time-wheel-container').forEach(c => c.remove());
    }
});

function createWheel(input) {
    const rect = input.getBoundingClientRect();
    const container = document.createElement('div');
    container.className = 'time-wheel-container';
    container.style.position = 'absolute';
    container.style.left = rect.left + 'px';
    container.style.top = (rect.bottom + window.scrollY) + 'px';
    container.style.zIndex = 9999;

    // Create hour and minute wheels
    const hourWheel = document.createElement('div');
    hourWheel.className = 'wheel hour-wheel';
    // Create repeated series so wheel feels infinite
    const hours = [];
    for (let h = 0; h < 24; h++) hours.push(String(h).padStart(2,'0'));
    for (let rep = 0; rep < 6; rep++) { // repeat several times
        hours.forEach(h => {
            const item = document.createElement('div');
            item.className = 'wheel-item';
            item.textContent = h;
            hourWheel.appendChild(item);
        });
    }

    const minuteWheel = document.createElement('div');
    minuteWheel.className = 'wheel minute-wheel';
    const minutes = [];
    for (let m = 0; m < 60; m += 1) minutes.push(String(m).padStart(2,'0'));
    for (let rep = 0; rep < 6; rep++) {
        minutes.forEach(m => {
            const item = document.createElement('div');
            item.className = 'wheel-item';
            item.textContent = m;
            minuteWheel.appendChild(item);
        });
    }

    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'btn btn-primary time-wheel-apply';
    btn.textContent = 'Set';

    container.appendChild(hourWheel);
    container.appendChild(minuteWheel);
    container.appendChild(btn);

    document.body.appendChild(container);

    // Try to set initial selection from input value
    const parts = (input.value || '').split(':');
    const initH = parts[0] ? parseInt(parts[0], 10) : 9;
    const initM = parts[1] ? parseInt(parts[1], 10) : 0;

    // Scroll to initial positions (centered in the middle repetition)
    const itemHeight = 28;
    const centerRep = 2; // middle of repeated blocks
    hourWheel.scrollTop = (centerRep * 24 + initH - 2) * itemHeight;
    minuteWheel.scrollTop = (centerRep * 60 + initM - 2) * itemHeight;

    // make wheels focusable for keyboard interaction
    hourWheel.tabIndex = 0;
    minuteWheel.tabIndex = 0;

    // center indicator overlay
    const centerIndicatorH = document.createElement('div');
    centerIndicatorH.className = 'time-wheel-center';
    hourWheel.appendChild(centerIndicatorH);
    const centerIndicatorM = document.createElement('div');
    centerIndicatorM.className = 'time-wheel-center';
    minuteWheel.appendChild(centerIndicatorM);

    // click handlers
    // Make items selectable by click
    container.querySelectorAll('.wheel-item').forEach(item => {
        item.addEventListener('click', () => {
            const parent = item.parentNode;
            parent.querySelectorAll('.wheel-item.selected').forEach(i => i.classList.remove('selected'));
            item.classList.add('selected');
            // snap selected into center
            parent.scrollTop = item.offsetTop - (parent.clientHeight/2) + (item.clientHeight/2);
        });
    });

    // Add snap on scroll (debounced)
    function addSnap(wheel) {
        let timer;
        wheel.addEventListener('scroll', () => {
            clearTimeout(timer);
            timer = setTimeout(() => {
                const items = Array.from(wheel.querySelectorAll('.wheel-item'));
                const centerY = wheel.scrollTop + wheel.clientHeight/2;
                let closest = items[0];
                let minDiff = Infinity;
                items.forEach(it => {
                    const diff = Math.abs(it.offsetTop + it.clientHeight/2 - centerY);
                    if (diff < minDiff) { minDiff = diff; closest = it; }
                });
                wheel.scrollTop = closest.offsetTop - (wheel.clientHeight/2) + (closest.clientHeight/2);
                wheel.querySelectorAll('.wheel-item.selected').forEach(i => i.classList.remove('selected'));
                closest.classList.add('selected');
            }, 150);
        });
    }

    addSnap(hourWheel);
    addSnap(minuteWheel);

    // ensure initial selection after scroll settles
    function pickInitial(wheel) {
        const items = Array.from(wheel.querySelectorAll('.wheel-item'));
        const centerY = wheel.scrollTop + wheel.clientHeight/2;
        let closest = items[0];
        let minDiff = Infinity;
        items.forEach(it => {
            const diff = Math.abs(it.offsetTop + it.clientHeight/2 - centerY);
            if (diff < minDiff) { minDiff = diff; closest = it; }
        });
        wheel.querySelectorAll('.wheel-item.selected').forEach(i => i.classList.remove('selected'));
        closest.classList.add('selected');
    }

    // small delay to let scrollTop settle then pick initial
    setTimeout(() => { pickInitial(hourWheel); pickInitial(minuteWheel); }, 60);

    // keyboard support: arrow up/down / page up/down
    function addKeyboard(wheel) {
        wheel.addEventListener('keydown', (e) => {
            if (['ArrowUp','ArrowDown','PageUp','PageDown','Home','End'].includes(e.key)) {
                e.preventDefault();
                const step = (e.key === 'PageUp' || e.key === 'PageDown') ? 5 : 1;
                let delta = 0;
                if (e.key === 'ArrowUp' || e.key === 'PageUp') delta = -step * itemHeight;
                if (e.key === 'ArrowDown' || e.key === 'PageDown') delta = step * itemHeight;
                if (e.key === 'Home') { wheel.scrollTop = 0; }
                else if (e.key === 'End') { wheel.scrollTop = wheel.scrollHeight; }
                else { wheel.scrollBy({ top: delta, behavior: 'smooth' }); }
            }
        });
    }

    addKeyboard(hourWheel);
    addKeyboard(minuteWheel);

    btn.addEventListener('click', () => {
        const selH = hourWheel.querySelector('.wheel-item.selected');
        const selM = minuteWheel.querySelector('.wheel-item.selected');
        const h = selH ? selH.textContent : String(initH).padStart(2,'0');
        const m = selM ? selM.textContent : String(initM).padStart(2,'0');
        input.value = `${h}:${m}`;
        // notify change and blur to trigger form frameworks
        try { input.dispatchEvent(new Event('change', { bubbles: true })); } catch (e) {}
        input.blur();
        container.remove();
    });

    return container;
}

// Attach to dynamic inputs
function attachTimeWheels() {
    document.querySelectorAll('input.timewheel').forEach(inp => {
        if (inp._timewheelAttached) return;
        inp._timewheelAttached = true;
        inp.addEventListener('focus', (e) => {
            // Remove others
            document.querySelectorAll('.time-wheel-container').forEach(c => c.remove());
            createWheel(inp);
        });
        inp.addEventListener('click', (e) => {
            e.stopPropagation();
            // focus will create wheel
        });
    });
}

// Run on load
window.addEventListener('load', attachTimeWheels);

// Use a MutationObserver to attach to dynamically added inlines instead of polling
const observer = new MutationObserver((mutations) => {
    // small debounce
    if (observer._scheduled) return;
    observer._scheduled = true;
    setTimeout(() => { attachTimeWheels(); observer._scheduled = false; }, 60);
});
observer.observe(document.body, { childList: true, subtree: true });
