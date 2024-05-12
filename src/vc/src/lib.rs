extern crate chrono;
extern crate similar;
extern crate pyo3;

use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use chrono::{DateTime, Utc, TimeZone};
use similar::{ChangeTag, TextDiff};
use std::collections::{HashMap, BTreeMap};
use std::thread;
use std::time::Duration;

type Change = (String, String);
type Save = (String, String);

#[pyclass]
struct VersionControl {
    changes: HashMap<String, Vec<Change>>,
    saves: HashMap<String, Vec<Save>>,
}

#[pymethods]
impl VersionControl {
    #[new]
    pub fn new() -> Self {
        VersionControl {
            changes: HashMap::new(),
            saves: HashMap::new(),
        }
    }

    pub fn add_change(&mut self, path: &str, text: String) {
        let timestamp = Utc::now().format("%Y-%m-%d %H:%M:%S").to_string();
        let change = (timestamp, text);

        self.changes.entry(path.to_string()).or_insert_with(Vec::new).push(change);
    }

    pub fn add_save(&mut self, path: &str, text: String) {
        let timestamp = Utc::now().format("%Y-%m-%d %H:%M:%S").to_string();
        let save = (timestamp, text);

        self.saves.entry(path.to_string()).or_insert_with(Vec::new).push(save);
    }

    pub fn get_changes(&self, path: &str) -> Vec<Change> {
        self.changes.get(path).cloned().unwrap_or_else(Vec::new)
    }

    pub fn get_saves(&self, path: &str) -> Vec<Save> {
        self.saves.get(path).cloned().unwrap_or_else(Vec::new)
    }

    pub fn get_difference(&self, path: &str) -> String {
        let last_change = self.changes.get(path).and_then(|changes| changes.last());
        let last_save = self.saves.get(path).and_then(|saves| saves.last());

        match (last_change, last_save) {
            (Some((_, change_text)), Some((_, save_text))) => {
                let change_count = change_text.chars().count();
                let save_count = save_text.chars().count();

                let added = change_count.saturating_sub(save_count);  
                let removed = save_count.saturating_sub(change_count);

                let mut result = String::new();
                if added > 0 {
                    result.push_str(&format!("Added {} character(s)\n", added));
                }
                if removed > 0 {
                    result.push_str(&format!("Removed {} character(s)\n", removed));
                }
                if result.is_empty() {
                    result = "No changes".to_string();
                }
                result
            }
            _ => "No comparable entries found.".to_string(),
        }
    }

    pub fn get_sorted_changes(&self, path: &str) -> BTreeMap<String, BTreeMap<String, Vec<String>>> {
        let mut sorted = BTreeMap::new();
        if let Some(changes) = self.changes.get(path) {
            for (timestamp, text) in changes {
                let dt = Utc.datetime_from_str(timestamp, "%Y-%m-%d %H:%M:%S").unwrap();
                let day_key = dt.format("%B %eth:").to_string();
                let time_key = dt.format("%H:%M:%S").to_string();

                sorted.entry(day_key)
                    .or_insert_with(BTreeMap::new)
                    .entry(time_key)
                    .or_insert_with(Vec::new)
                    .push(text.clone());
            }
        }
        sorted
    }
}

#[pymodule]
fn vc(py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<VersionControl>()?;
    Ok(())
}

// fn normalize_path(path: &str) -> String {
//     path.replace("\\", "/")
// }
