# ConsultBae-AI-Assignment
Its an assignment for AI Automation Analyst / Developer at ConsultBee which includes 5 tasks 


##Task_1:

## Overview
This pipeline extracts raw, messy candidate data from three disparate CSV sources (Naukri, Gig Workers, and CBNexus), normalizes the fields, and executes a cascading matching logic to resolve duplicate entities. The final output is a pristine set of unique "Golden Records" stored in a relational MySQL database.

## Project Structure
*   **`normalize.py`**: Contains pure functions for data cleaning (phone normalization, standardizing names/cities, handling shifted CSV rows, and fixing mixed CTC formats).
*   **`match.py`**: The Entity Resolution engine. It merges records across the three sources based on primary keys (Email and Phone) and tracks data lineage (`merged_sources`).
*   **`db.py`**: SQLAlchemy ORM definitions for the database schema. Ensures referential integrity between the Hub table (`PERSON`) and the child source tables.
*   **`ingest.py`**: The main orchestrator script. It extracts the raw data, applies the cleaning and matching logic, and loads the final Golden Records into MySQL.
*   **`.env`**: (Ignored in Git) Stores local MySQL credentials.

## Prerequisites
*   Python 3.8+
*   MySQL Server (running locally)

## Setup & Installation

**1. Install Dependencies**
```bash
pip install -r requirements.txt