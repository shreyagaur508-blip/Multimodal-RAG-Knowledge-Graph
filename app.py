import os
import sys

import fitz
import streamlit as st


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = os.path.dirname(
    os.path.abspath(__file__)
)

sys.path.insert(0, PROJECT_ROOT)


# ============================================================
# DIRECTORIES
# ============================================================

PDF_DIR = os.path.join(
    PROJECT_ROOT,
    "data",
    "pdfs"
)

PAGES_DIR = os.path.join(
    PROJECT_ROOT,
    "data",
    "pages"
)

INDEX_DIR = os.path.join(
    PROJECT_ROOT,
    "indexes"
)


os.makedirs(PDF_DIR, exist_ok=True)
os.makedirs(PAGES_DIR, exist_ok=True)
os.makedirs(INDEX_DIR, exist_ok=True)


# ============================================================
# STREAMLIT CONFIG
# ============================================================

st.set_page_config(
    page_title="Multimodal RAG + Knowledge Graph",
    page_icon="📚",
    layout="wide"
)


# ============================================================
# TITLE
# ============================================================

st.title("📚 Multimodal RAG + Knowledge Graph")

st.markdown(
    """
    Ask questions about PDF documents using:

    **🖼️ Visual Retrieval + 🧠 Knowledge Graph + 🔗 Hybrid Retrieval**
    """
)


# ============================================================
# PDF RENDERER
# ============================================================

def render_pdf(pdf_path):

    # Remove old page images
    for filename in os.listdir(PAGES_DIR):

        file_path = os.path.join(
            PAGES_DIR,
            filename
        )

        if filename.lower().endswith(
            (".png", ".jpg", ".jpeg")
        ):

            try:
                os.remove(file_path)
            except Exception:
                pass


    document = fitz.open(pdf_path)

    page_paths = []


    for page_number, page in enumerate(
        document,
        start=1
    ):

        # High-resolution rendering
        matrix = fitz.Matrix(
            2,
            2
        )

        pixmap = page.get_pixmap(
            matrix=matrix,
            alpha=False
        )

        output_path = os.path.join(
            PAGES_DIR,
            f"page_{page_number}.png"
        )

        pixmap.save(
            output_path
        )

        page_paths.append(
            output_path
        )


    document.close()

    return page_paths


# ============================================================
# VISUAL INDEX
# ============================================================

def build_visual_index():

    import subprocess

    indexer_path = os.path.join(
        PROJECT_ROOT,
        "ingestion",
        "visual_indexer.py"
    )

    result = subprocess.run(
        [
            sys.executable,
            indexer_path
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True
    )

    return (
        result.returncode == 0,
        result.stdout,
        result.stderr
    )


# ============================================================
# LOAD RETRIEVAL SYSTEM
# ============================================================

@st.cache_resource
def load_system():

    from retrieval.hybrid_retriever import (
        HybridRetriever
    )

    from generation.vlm import (
        VLMGenerator
    )

    retriever = HybridRetriever()

    generator = VLMGenerator()

    return retriever, generator


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("📄 Document")

uploaded_file = st.sidebar.file_uploader(
    "Upload a PDF",
    type=["pdf"]
)


top_k = st.sidebar.slider(
    "Pages to retrieve",
    min_value=1,
    max_value=3,
    value=3
)


# ============================================================
# PROCESS PDF
# ============================================================

if uploaded_file:

    st.sidebar.success(
        f"Selected:\n{uploaded_file.name}"
    )


    if st.sidebar.button(
        "⚙️ Process PDF",
        type="primary"
    ):

        # ----------------------------------------------------
        # SAVE PDF
        # ----------------------------------------------------

        pdf_path = os.path.join(
            PDF_DIR,
            uploaded_file.name
        )


        with open(
            pdf_path,
            "wb"
        ) as file:

            file.write(
                uploaded_file.getbuffer()
            )


        st.success(
            f"✅ PDF saved: {uploaded_file.name}"
        )


        # ----------------------------------------------------
        # RENDER PDF
        # ----------------------------------------------------

        with st.spinner(
            "Rendering PDF pages..."
        ):

            try:

                page_paths = render_pdf(
                    pdf_path
                )

                st.success(
                    f"✅ PDF rendering successful! "
                    f"{len(page_paths)} page(s) created."
                )

            except Exception as error:

                st.error(
                    "❌ PDF rendering failed."
                )

                st.exception(error)

                st.stop()


        # ----------------------------------------------------
        # VISUAL INDEX
        # ----------------------------------------------------

        with st.spinner(
            "Building visual index..."
        ):

            success, output, error = (
                build_visual_index()
            )


        if success:

            st.success(
                "✅ Visual index created successfully!"
            )

        else:

            st.error(
                "❌ Visual indexing failed."
            )

            if error:
                st.code(error)

            st.stop()


        # ----------------------------------------------------
        # SHOW PAGES
        # ----------------------------------------------------

        st.subheader(
            "📄 Processed Pages"
        )

        cols = st.columns(
            min(len(page_paths), 3)
        )


        for index, page_path in enumerate(
            page_paths
        ):

            with cols[index % len(cols)]:

                st.image(
                    page_path,
                    caption=f"Page {index + 1}",
                    use_container_width=True
                )


# ============================================================
# LOAD SYSTEM
# ============================================================

try:

    retriever, generator = load_system()

except Exception as error:

    st.error(
        "Could not initialize retrieval system."
    )

    st.exception(error)

    st.stop()


# ============================================================
# QUESTION
# ============================================================

st.header("🔎 Ask a Question")


question = st.text_input(
    "Enter your question",
    placeholder="Example: What is machine learning?"
)


# ============================================================
# SEARCH
# ============================================================

if st.button(
    "🔍 Search",
    type="primary"
):

    if not question.strip():

        st.warning(
            "Please enter a question."
        )

        st.stop()


    # --------------------------------------------------------
    # HYBRID RETRIEVAL
    # --------------------------------------------------------

    with st.spinner(
        "Running hybrid retrieval..."
    ):

        try:

            results = retriever.retrieve(
                question,
                top_k=top_k
            )

        except Exception as error:

            st.error(
                "❌ Retrieval failed."
            )

            st.exception(error)

            st.stop()


    # --------------------------------------------------------
    # ANSWER
    # --------------------------------------------------------

    st.header("💬 Answer")


    try:

        answer = generator.generate(
            question,
            results
        )

        st.success(
            answer
        )

    except Exception as error:

        st.error(
            "Answer generation failed."
        )

        st.exception(error)


    # --------------------------------------------------------
    # RETRIEVED PAGES
    # --------------------------------------------------------

    st.header(
        "📄 Retrieved Sources"
    )


    if not results:

        st.info(
            "No relevant pages found."
        )

    else:

        for result in results:

            page_number = result[
                "page_number"
            ]

            score = result[
                "score"
            ]

            source = result[
                "source"
            ]

            image_path = result[
                "image_path"
            ]


            with st.expander(
                f"Page {page_number} | "
                f"{source} | "
                f"Score: {score:.4f}",
                expanded=True
            ):

                col1, col2 = st.columns(
                    [2, 1]
                )


                with col1:

                    if os.path.exists(
                        image_path
                    ):

                        st.image(
                            image_path,
                            caption=(
                                f"Retrieved Page "
                                f"{page_number}"
                            ),
                            use_container_width=True
                        )

                    else:

                        st.warning(
                            "Page image not found."
                        )


                with col2:

                    st.write(
                        "**Page:**",
                        page_number
                    )

                    st.write(
                        "**Score:**",
                        f"{score:.4f}"
                    )

                    st.write(
                        "**Retrieval source:**",
                        source
                    )


                    if "graph_entity" in result:

                        st.write(
                            "**Knowledge Graph Entity:**",
                            result[
                                "graph_entity"
                            ]
                        )


# ============================================================
# ABOUT
# ============================================================

with st.expander(
    "ℹ️ About this project"
):

    st.write(
        """
        This project demonstrates a Multimodal RAG system
        combined with a Knowledge Graph.

        PDF documents are rendered into page images.
        Visual retrieval identifies relevant pages.
        Neo4j provides structured entity-based retrieval.
        The Hybrid Retriever combines both sources.
        """
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Multimodal RAG + Knowledge Graph | "
    "Local CPU implementation"
)