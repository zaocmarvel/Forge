const API_URL = "http://localhost:8000/stories";

// DOM Elements
const els = {
    storyForm: document.getElementById('storyForm'),
    title: document.getElementById('title'),
    genre: document.getElementById('genre'),
    prompt: document.getElementById('prompt'),
    createBtn: document.getElementById('createBtn'),
    storiesList: document.getElementById('storiesList'),
    storyCount: document.getElementById('storyCount'),
    emptyState: document.getElementById('emptyState'),
    
    // Modal
    modal: document.getElementById('storyModal'),
    modalTitle: document.getElementById('modalTitle'),
    modalGenre: document.getElementById('modalGenre'),
    storyViewer: document.getElementById('storyViewer'),
    closeModal: document.getElementById('closeModal'),
    downloadBtn: document.getElementById('downloadBtn'),
    continueBtn: document.getElementById('continueBtn'),
    continuePrompt: document.getElementById('continuePrompt')
};

let currentStoryId = null;

// --- Init ---
document.addEventListener('DOMContentLoaded', fetchStories);

// --- Event Listeners ---
els.storyForm.addEventListener('submit', handleCreateStory);
els.closeModal.addEventListener('click', closeModal);
els.continueBtn.addEventListener('click', handleContinueStory);
els.downloadBtn.addEventListener('click', handleDownload);

// Close modal on backdrop click
els.modal.addEventListener('click', (e) => {
    if (e.target === els.modal) closeModal();
});

// --- API Functions ---

async function fetchStories() {
    try {
        const res = await fetch(API_URL);
        const stories = await res.json();
        renderLibrary(stories);
    } catch (err) {
        console.error("Failed to load stories", err);
    }
}

async function handleCreateStory(e) {
    e.preventDefault();
    setLoading(els.createBtn, true);

    const payload = {
        title: els.title.value,
        genre: els.genre.value,
        prompt: els.prompt.value
    };

    try {
        const res = await fetch(`${API_URL}/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!res.ok) throw new Error("Failed to forge story");

        const story = await res.json();
        
        // Reset Form
        els.storyForm.reset();
        
        // Refresh List & Open Story
        await fetchStories();
        openStory(story.id);

    } catch (err) {
        alert(err.message);
    } finally {
        setLoading(els.createBtn, false);
    }
}

async function handleContinueStory() {
    if (!currentStoryId) return;
    setLoading(els.continueBtn, true);

    try {
        const res = await fetch(`${API_URL}/${currentStoryId}/chapters`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ 
                story_id: currentStoryId,
                instructions: els.continuePrompt.value || "Continue story naturally"
            })
        });

        if (!res.ok) throw new Error("Failed to generate chapter");

        const chapter = await res.json();
        
        // Append new chapter to view
        appendChapter(chapter);
        els.continuePrompt.value = "";
        
        // Scroll to bottom
        els.storyViewer.scrollTop = els.storyViewer.scrollHeight;

    } catch (err) {
        alert(err.message);
    } finally {
        setLoading(els.continueBtn, false);
    }
}

async function openStory(id) {
    currentStoryId = id;
    els.storyViewer.innerHTML = '<div style="text-align:center; padding:2rem; color:#666;">Loading Codex...</div>';
    els.modal.classList.add('active');

    try {
        const res = await fetch(`${API_URL}/${id}`);
        if (!res.ok) throw new Error("Story not found");
        
        const story = await res.json();
        
        // Update Header
        els.modalTitle.textContent = story.title;
        els.modalGenre.textContent = story.genre;
        
        // Render Chapters
        els.storyViewer.innerHTML = '';
        story.chapters.forEach(appendChapter);

    } catch (err) {
        els.storyViewer.innerHTML = `<p style="color:red; text-align:center">${err.message}</p>`;
    }
}

async function handleDownload() {
    if (!currentStoryId) return;
    
    // Visual feedback on icon
    els.downloadBtn.classList.add('loading');
    
    try {
        const res = await fetch(`${API_URL}/${currentStoryId}/download`);
        if (!res.ok) throw new Error("Download failed");
        
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        
        // Get filename
        const disposition = res.headers.get('Content-Disposition');
        let filename = `story-${currentStoryId}.txt`;
        if (disposition && disposition.includes('filename=')) {
            filename = disposition.split('filename=')[1].replace(/"/g, '');
        }
        
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        
        window.URL.revokeObjectURL(url);
        a.remove();
    } catch (err) {
        alert(err.message);
    } finally {
        els.downloadBtn.classList.remove('loading');
    }
}

// --- UI Helpers ---

function renderLibrary(stories) {
    els.storyCount.textContent = `${stories.length} Stories`;
    
    if (stories.length === 0) {
        els.emptyState.classList.remove('hidden');
        els.storiesList.innerHTML = '';
        return;
    }

    els.emptyState.classList.add('hidden');
    els.storiesList.innerHTML = stories.map(story => `
        <article class="story-card" onclick="openStory(${story.id})">
            <div>
                <span class="tag">${story.genre}</span>
                <h3 style="margin: 0.5rem 0 0 0; font-size: 1.1rem;">${story.title}</h3>
                <p style="color: var(--text-muted); font-size: 0.9rem; margin-top: 0.5rem; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;">
                    ${story.prompt}
                </p>
            </div>
            <div class="card-meta">
                <span>${new Date(story.created_at).toLocaleDateString()}</span>
                <span>Open &rarr;</span>
            </div>
        </article>
    `).join('');
}

function appendChapter(chapter) {
    const html = `
        <div class="chapter">
            <div class="chapter-title">Chapter ${chapter.chapter_number}: ${chapter.title}</div>
            <div class="chapter-content">${chapter.content}</div>
        </div>
    `;
    els.storyViewer.insertAdjacentHTML('beforeend', html);
}

function closeModal() {
    els.modal.classList.remove('active');
    currentStoryId = null;
}

function setLoading(btnElement, isLoading) {
    if (isLoading) {
        btnElement.classList.add('loading');
        btnElement.disabled = true;
    } else {
        btnElement.classList.remove('loading');
        btnElement.disabled = false;
    }
}