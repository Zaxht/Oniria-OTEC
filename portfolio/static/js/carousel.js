document.querySelectorAll('[data-carousel]').forEach(carousel => {
  const track = carousel.querySelector('.carousel-track');
  const controls = carousel.querySelector('.carousel-controls');
  const originals = [...track.children];
  const count = originals.length;
  if (!count) return;
  const previous = controls.querySelector('[data-direction="-1"]');
  const next = controls.querySelector('[data-direction="1"]');
  const position = controls.querySelector('.carousel-position');
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  let step = 0, cycle = 0, active = 0, lastWidth = 0, frame, settle, resetting = false;
  let drag = null, dragged = false;
  // Keep the real set in the middle; visual buffers are excluded from keyboard and screen readers.
  originals.forEach((card, index) => { card.dataset.courseIndex = index; });
  if (count > 1) {
    const copySet = () => originals.map(card => {
      const copy = card.cloneNode(true);
      copy.dataset.carouselCopy = '';
      copy.setAttribute('aria-hidden', 'true');
      copy.querySelectorAll('a,button,input,[tabindex]').forEach(el => el.setAttribute('tabindex', '-1'));
      copy.querySelectorAll('[id]').forEach(el => el.removeAttribute('id'));
      return copy;
    });
    track.prepend(...copySet(), ...copySet());
    track.append(...copySet(), ...copySet());
    carousel.classList.add('is-endless');
    controls.hidden = false;
    previous.disabled = next.disabled = false;
    carousel.querySelector('.carousel-hint').innerHTML = 'Sigue tu curiosidad <span aria-hidden="true">∞</span>';
  } else {
    carousel.querySelector('.carousel-hint').textContent = 'Tu próxima exploración';
  }
  const jump = left => {
    resetting = true;
    track.classList.add('is-repositioning');
    track.scrollTo({left, behavior: 'instant'});
    requestAnimationFrame(() => {
      track.classList.remove('is-repositioning');
      resetting = false;
    });
  };
  const update = () => {
    if (!step) return;
    const index = Math.round(track.scrollLeft / step);
    active = ((index % count) + count) % count;
    position.textContent = `${String(active + 1).padStart(2, '0')} / ${String(count).padStart(2, '0')}`;
    track.querySelectorAll('.course-card').forEach(card => card.classList.toggle('is-current', Number(card.dataset.courseIndex) === active));
  };
  const normalize = () => {
    if (count < 2 || !cycle || resetting || drag) return;
    const focusedLink = track.contains(document.activeElement) && document.activeElement !== track;
    if (focusedLink) return;
    const nearest = Math.round(track.scrollLeft / step);
    const logical = ((nearest % count) + count) % count;
    const remainder = track.scrollLeft - nearest * step;
    const target = cycle * 2 + logical * step + remainder;
    if (Math.abs(target - track.scrollLeft) > 5) jump(target);
  };
  const measure = () => {
    if (lastWidth === track.clientWidth) return;
    lastWidth = track.clientWidth;
    step = parseFloat(getComputedStyle(originals[0]).width) + (parseFloat(getComputedStyle(track).gap) || 0);
    cycle = step * count;
    jump(count > 1 ? cycle * 2 + active * step : 0);
    update();
  };
  const move = direction => {
    if (!step || count < 2) return;
    clearTimeout(settle);
    track.scrollBy({left: direction * step, behavior: reduced.matches ? 'instant' : 'smooth'});
  };
  previous.addEventListener('click', () => move(-1));
  next.addEventListener('click', () => move(1));
  track.addEventListener('keydown', event => {
    if (event.target !== track || !['ArrowLeft', 'ArrowRight'].includes(event.key)) return;
    event.preventDefault();
    move(event.key === 'ArrowRight' ? 1 : -1);
  });
  track.addEventListener('scroll', () => {
    cancelAnimationFrame(frame);
    frame = requestAnimationFrame(() => {
      update();
      if (!resetting && count > 1 && (track.scrollLeft < cycle * .5 || track.scrollLeft > cycle * 3.5)) normalize();
    });
    clearTimeout(settle);
    settle = setTimeout(normalize, 180);
  }, {passive: true});
  track.addEventListener('pointerdown', event => {
    if (event.pointerType !== 'mouse' || event.button !== 0) return;
    dragged = false;
    drag = {x: event.clientX, y: event.clientY, left: track.scrollLeft, id: event.pointerId};
  });
  track.addEventListener('pointermove', event => {
    if (!drag) return;
    const dx = event.clientX - drag.x;
    if (!dragged && Math.abs(dx) < 7) return;
    if (!dragged && Math.abs(event.clientY - drag.y) > Math.abs(dx)) { drag = null; return; }
    dragged = true;
    track.classList.add('is-dragging');
    track.setPointerCapture(drag.id);
    track.scrollLeft = drag.left - dx;
  });
  const endDrag = () => {
    if (!drag) return;
    const id = drag.id;
    drag = null;
    if (track.hasPointerCapture(id)) track.releasePointerCapture(id);
    track.classList.remove('is-dragging');
    if (dragged) {
      track.focus({preventScroll: true});
      track.scrollTo({left: Math.round(track.scrollLeft / step) * step, behavior: reduced.matches ? 'instant' : 'smooth'});
      settle = setTimeout(normalize, 200);
    }
  };
  track.addEventListener('pointerup', endDrag);
  track.addEventListener('pointercancel', endDrag);
  track.addEventListener('lostpointercapture', endDrag);
  track.addEventListener('dragstart', event => event.preventDefault());
  track.addEventListener('click', event => {
    if (dragged) { event.preventDefault(); event.stopPropagation(); dragged = false; }
  }, true);
  track.querySelectorAll('.course-card').forEach(card => {
    card.addEventListener('pointermove', event => {
      if (reduced.matches || drag || event.pointerType !== 'mouse') return;
      const box = card.getBoundingClientRect();
      card.style.setProperty('--tilt-y', `${((event.clientX - box.left) / box.width - .5) * 6}deg`);
      card.style.setProperty('--tilt-x', `${(.5 - (event.clientY - box.top) / box.height) * 4}deg`);
    });
    card.addEventListener('pointerleave', () => {
      card.style.setProperty('--tilt-x', '0deg');
      card.style.setProperty('--tilt-y', '0deg');
    });
  });
  new ResizeObserver(measure).observe(track);
  measure();
});
