extern crate chrono;
extern crate similar;
// extern crate pyo3;

// use pyo3::prelude::*;
// use pyo3::wrap_pyfunction;
use chrono::{DateTime, Utc, TimeZone};
use similar::{ChangeTag, TextDiff};
use std::collections::HashMap;

type Change = (String, String);
type Save = (String, String);

//#[pyclass]
struct VersionControl {
    changes: HashMap<String, Vec<Change>>,
    saves: HashMap<String, Vec<Save>>,
}

//#[pymethods]
impl VersionControl {
    //#[new]
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
                let diff = TextDiff::from_lines(save_text, change_text);
                let mut result = String::new();

                for change in diff.iter_all_changes() {
                    let sign = match change.tag() {
                        ChangeTag::Delete => "-",
                        ChangeTag::Insert => "+",
                        ChangeTag::Equal => " ",
                    };
                    result.push_str(&format!("{}{}\n", sign, change));
                }
                result
            },
            _ => "No comparable entries found.".to_string(),
        }
    }
}

// #[pymodule]
// fn vc(py: Python, m: &PyModule) -> PyResult<()> {
//     m.add_class::<VersionControl>()?;
//     Ok(())
// }

// fn normalize_path(path: &str) -> String {
//     path.replace("\\", "/")
// }
fn main() {
    let mut vc = VersionControl::new();
    
    vc.add_change("file1.txt", "Initial content".to_string());
    vc.add_save("file1.txt", "Initial content".to_string());
    vc.add_change("file1.txt", "Initial contentt".to_string());

    let changes = vc.get_changes("file1.txt");
    for (timestamp, text) in changes {
        println!("At {}: {}", timestamp, text);
    }
    let saves = vc.get_saves("file1.txt");
    for (timestamp, text) in saves {
        println!("At {}: {}", timestamp, text);
    }

    let diff = vc.get_difference("file1.txt");
    println!("Differences:\n{}", diff);
}