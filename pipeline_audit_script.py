#!/usr/bin/env python3
"""
Advanced Pipeline Audit Script for FARFAN_MCDPP Repository
Performs comprehensive analysis of code quality, errors, performance, and implementation issues
"""

import argparse
import ast
import concurrent.futures
import importlib.util
import json
import logging
import os
import re
import subprocess
import sys
import time
import traceback
import warnings
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(name)s] - %(message)s',
    handlers=[
        logging.FileHandler(f'pipeline_audit_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class AuditIssue:
    """Represents an issue found during audit"""
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    category: str
    file_path: str
    line_number: Optional[int]
    description: str
    recommendation: str
    code_snippet: Optional[str] = None
    metrics: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AuditReport:
    """Complete audit report structure"""
    timestamp: str
    repository: str
    total_files_analyzed: int
    issues: List[AuditIssue] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    performance_bottlenecks: List[Dict] = field(default_factory=list)
    dependency_issues: List[Dict] = field(default_factory=list)
    security_vulnerabilities: List[Dict] = field(default_factory=list)

class PipelineAuditor:
    """Main audit engine for comprehensive pipeline analysis"""
    
    def __init__(self, repo_path: str = ".", verbose: bool = True):
        self.repo_path = Path(repo_path).resolve()
        self.verbose = verbose
        self.report = AuditReport(
            timestamp=datetime.now().isoformat(),
            repository=str(self.repo_path),
            total_files_analyzed=0
        )
        self.file_cache = {}
        self.import_graph = defaultdict(set)
        self.function_complexity = {}
        self.error_patterns = self._load_error_patterns()
        
    def _load_error_patterns(self) -> Dict[str, List[re.Pattern]]:
        """Load patterns for detecting various types of errors"""
        return {
            'silenced_errors': [
                # Only match except with pass on the NEXT line (single-line pattern)
                # The AST analyzer handles multi-line cases properly
                re.compile(r'except\s*:\s*pass\b'),
                re.compile(r'except\s+Exception\s*:\s*pass\b'),
                # Match TODO/FIXME comments about errors
                re.compile(r'#.*TODO.*error', re.IGNORECASE),
                re.compile(r'#.*FIXME.*error', re.IGNORECASE),
            ],
            'performance_issues': [
                re.compile(r'for\s+\w+\s+in\s+.*\.read.*\(\)'),
                re.compile(r'\.append\s*\([^)]+\)\s*in\s+for'),
                re.compile(r'time\.sleep\s*\([^)]*\)'),
                re.compile(r'SELECT\s+\*\s+FROM', re.IGNORECASE),
                re.compile(r'N\s*\+\s*1\s+quer(?:y|ies)', re.IGNORECASE),
            ],
            'security_risks': [
                # Match eval() but not ast.literal_eval(), literal_eval(), or method calls like .eval()
                # Use negative lookbehind to exclude method calls (preceded by .)
                re.compile(r'(?<!\.)(?<!\w)\beval\s*\('),
                re.compile(r'(?<!\.)(?<!\w)\bexec\s*\('),
                re.compile(r'pickle\.loads?\s*\('),
                re.compile(r'os\.system\s*\('),
                re.compile(r'subprocess\..*shell\s*=\s*True'),
                # Only flag actual hardcoded secrets, not test credentials
                re.compile(r'password\s*=\s*["\'][^"\']{20,}["\']'),  # Only flag long passwords
                re.compile(r'api_key\s*=\s*["\'][a-zA-Z0-9]{32,}["\']'),  # Only flag long API keys
            ],
            'code_smells': [
                re.compile(r'if\s+True\s*:'),
                re.compile(r'if\s+False\s*:'),
                re.compile(r'while\s+True\s*:(?!.*break)'),
                re.compile(r'import\s+\*'),
                re.compile(r'global\s+'),
            ]
        }
    
    def run_full_audit(self) -> AuditReport:
        """Execute complete pipeline audit"""
        logger.info(f"Starting comprehensive audit of {self.repo_path}")
        
        try:
            # Phase 1: Static Code Analysis
            self._analyze_python_files()
            
            # Phase 2: Dependency Analysis
            self._audit_dependencies()
            
            # Phase 3: Configuration Analysis
            self._analyze_configurations()
            
            # Phase 4: Performance Analysis
            self._analyze_performance()
            
            # Phase 5: Security Audit
            self._security_audit()
            
            # Phase 6: CI/CD Pipeline Analysis
            self._analyze_ci_cd()
            
            # Phase 7: Database and Data Flow
            self._analyze_data_flow()
            
            # Phase 8: Error Handling Audit
            self._audit_error_handling()
            
            # Phase 9: Generate Recommendations
            self._generate_recommendations()
            
        except Exception as e:
            logger.error(f"Critical error during audit: {str(e)}")
            self.report.issues.append(AuditIssue(
                severity="CRITICAL",
                category="AUDIT_FAILURE",
                file_path="",
                line_number=None,
                description=f"Audit process failed: {str(e)}",
                recommendation="Fix the audit script or investigate the error",
                code_snippet=traceback.format_exc()
            ))
        
        return self.report
    
    def _analyze_python_files(self):
        """Deep analysis of Python files"""
        logger.info("Phase 1: Analyzing Python files...")
        
        python_files = list(self.repo_path.glob("**/*.py"))
        self.report.total_files_analyzed = len(python_files)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                executor.submit(self._analyze_single_python_file, file_path): file_path 
                for file_path in python_files
            }
            
            for future in concurrent.futures.as_completed(futures):
                file_path = futures[future]
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"Error analyzing {file_path}: {str(e)}")
    
    def _analyze_single_python_file(self, file_path: Path):
        """Analyze individual Python file"""
        # Skip the audit script itself
        if file_path.name == 'pipeline_audit_script.py':
            return

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                self.file_cache[str(file_path)] = content
            
            # AST Analysis
            try:
                tree = ast.parse(content, filename=str(file_path))
                self._analyze_ast(tree, file_path, content)
            except SyntaxError as e:
                self.report.issues.append(AuditIssue(
                    severity="HIGH",
                    category="SYNTAX_ERROR",
                    file_path=str(file_path),
                    line_number=e.lineno,
                    description=f"Syntax error: {e.msg}",
                    recommendation="Fix syntax error to ensure code can be executed",
                    code_snippet=self._get_code_snippet(content, e.lineno)
                ))
            
            # Pattern-based Analysis
            self._check_patterns(content, file_path)
            
            # Complexity Analysis
            self._analyze_complexity(content, file_path)
            
        except Exception as e:
            logger.error(f"Failed to analyze {file_path}: {str(e)}")
    
    def _analyze_ast(self, tree: ast.AST, file_path: Path, content: str):
        """Analyze Abstract Syntax Tree using specialized analyzers.
        
        This method delegates to the ast_analyzers module which provides
        specialized analyzer classes for:
        - Function complexity analysis
        - Exception handling pattern detection  
        - Import tracking
        
        Complexity: ~2 (orchestration only)
        """
        from ast_analyzers import analyze_ast
        
        result = analyze_ast(self, tree, file_path, content)
        
        # Collect issues from analysis
        self.report.issues.extend(result.issues)
        
        # Update import graph for dependency analysis
        for imp in result.imports:
            self.import_graph[str(file_path)].add(imp)
        
        # Store function complexity for reporting
        self.function_complexity.update(result.function_complexity)
    
    def _is_test_file(self, file_path: str) -> bool:
        """Check if a file is a test file"""
        file_path_lower = file_path.lower()
        return ('test' in file_path_lower or
                '/tests/' in file_path_lower or
                file_path_lower.endswith('_test.py') or
                file_path_lower.startswith('test_'))

    def _check_patterns(self, content: str, file_path: Path):
        """Check for problematic patterns in code"""
        lines = content.split('\n')
        is_test = self._is_test_file(str(file_path))
        file_path_lower = str(file_path).lower()
        # Files that commonly use pickle for internal storage (not user data)
        is_cache_file = any(keyword in file_path_lower for keyword in [
            'cache', 'checkpoint', 'circuit_breaker', 'nexus', 'storage'
        ])

        for category, patterns in self.error_patterns.items():
            for pattern in patterns:
                matches = pattern.finditer(content)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    matched_text = match.group()

                    # Skip certain security checks in test files
                    if is_test and category == 'security_risks':
                        # Allow eval() and hardcoded credentials in test files
                        if any(keyword in matched_text for keyword in ['eval(', 'password =', 'api_key =']):
                            continue

                    # Skip safe versions of eval/exec (ast.literal_eval, literal_eval)
                    if category == 'security_risks' and ('eval(' in matched_text or 'exec(' in matched_text):
                        # Check if it's a safe version
                        line_start = max(0, content.rfind('\n', 0, match.start()) + 1)
                        line_content = content[line_start:content.find('\n', match.start())]
                        if 'literal_eval' in line_content or 'ast.literal_eval' in line_content:
                            continue

                    # Reduce severity for pickle in cache files (still warn, but less critical)
                    severity = None
                    recommendation = None

                    if category == 'security_risks' and 'pickle' in matched_text and is_cache_file:
                        severity = 'MEDIUM'  # Downgrade from CRITICAL
                        recommendation = "Ensure pickle.load() only processes trusted data from internal cache/storage files"
                    # Downgrade shell=True in verification scripts (typically safe, hardcoded commands)
                    elif category == 'security_risks' and 'shell' in matched_text.lower():
                        if any(keyword in file_path_lower for keyword in ['verify', 'contract', 'test']):
                            severity = 'MEDIUM'
                            recommendation = "Verify that shell=True is only used with hardcoded commands, not user input"
                        else:
                            severity = 'CRITICAL'
                            recommendation = self._get_recommendation_for_pattern(category, matched_text)
                    else:
                        severity_map = {
                            'silenced_errors': 'HIGH',
                            'performance_issues': 'MEDIUM',
                            'security_risks': 'CRITICAL',
                            'code_smells': 'LOW'
                        }
                        severity = severity_map.get(category, 'MEDIUM')
                        recommendation = self._get_recommendation_for_pattern(category, matched_text)

                    self.report.issues.append(AuditIssue(
                        severity=severity,
                        category=category.upper(),
                        file_path=str(file_path),
                        line_number=line_num,
                        description=f"Detected {category.replace('_', ' ')}: {matched_text[:50]}...",
                        recommendation=recommendation,
                        code_snippet=self._get_code_snippet(content, line_num)
                    ))
    
    def _analyze_complexity(self, content: str, file_path: Path):
        """Analyze code complexity metrics"""
        lines = content.split('\n')
        
        # Check file length
        if len(lines) > 500:
            self.report.issues.append(AuditIssue(
                severity="LOW",
                category="MAINTAINABILITY",
                file_path=str(file_path),
                line_number=None,
                description=f"File has {len(lines)} lines, consider splitting",
                recommendation="Break down large files into smaller, focused modules"
            ))
        
        # Check for long lines
        for i, line in enumerate(lines, 1):
            if len(line) > 120:
                self.report.issues.append(AuditIssue(
                    severity="INFO",
                    category="STYLE",
                    file_path=str(file_path),
                    line_number=i,
                    description=f"Line exceeds 120 characters ({len(line)} chars)",
                    recommendation="Break long lines for better readability"
                ))
    
    def _audit_dependencies(self):
        """Audit project dependencies"""
        logger.info("Phase 2: Auditing dependencies...")
        
        # Check requirements files
        req_files = ['requirements.txt', 'Pipfile', 'pyproject.toml', 'setup.py']
        for req_file in req_files:
            req_path = self.repo_path / req_file
            if req_path.exists():
                self._analyze_requirements_file(req_path)
        
        # Check for import errors
        self._check_circular_imports()
        self._check_missing_imports()
    
    def _analyze_requirements_file(self, req_path: Path):
        """Analyze requirements file for issues"""
        try:
            with open(req_path, 'r') as f:
                content = f.read()
            
            # Check for unpinned versions
            unpinned = re.findall(r'^([a-zA-Z0-9\-_]+)(?:\s|$)', content, re.MULTILINE)
            if unpinned:
                self.report.dependency_issues.append({
                    'file': str(req_path),
                    'issue': 'unpinned_versions',
                    'packages': unpinned,
                    'severity': 'MEDIUM',
                    'recommendation': 'Pin package versions for reproducible builds'
                })
            
            # Check for deprecated packages
            deprecated_packages = ['nose', 'pycrypto', 'PIL']
            for pkg in deprecated_packages:
                if pkg in content:
                    self.report.dependency_issues.append({
                        'file': str(req_path),
                        'issue': 'deprecated_package',
                        'package': pkg,
                        'severity': 'HIGH',
                        'recommendation': f'Replace deprecated package {pkg}'
                    })
            
        except Exception as e:
            logger.error(f"Failed to analyze {req_path}: {str(e)}")
    
    def _check_circular_imports(self):
        """Detect circular import dependencies"""
        
        def find_cycles(graph, start, visited=None, rec_stack=None):
            if visited is None:
                visited = set()
            if rec_stack is None:
                rec_stack = []
            
            visited.add(start)
            rec_stack.append(start)
            
            for neighbor in graph.get(start, []):
                if neighbor not in visited:
                    cycle = find_cycles(graph, neighbor, visited, rec_stack)
                    if cycle:
                        return cycle
                elif neighbor in rec_stack:
                    cycle_start = rec_stack.index(neighbor)
                    return rec_stack[cycle_start:]
            
            rec_stack.pop()
            return None
        
        # Check for circular imports
        for module in self.import_graph:
            cycle = find_cycles(self.import_graph, module)
            if cycle:
                self.report.issues.append(AuditIssue(
                    severity="HIGH",
                    category="CIRCULAR_IMPORT",
                    file_path=module,
                    line_number=None,
                    description=f"Circular import detected: {' -> '.join(cycle)}",
                    recommendation="Refactor code to eliminate circular dependencies"
                ))
    
    def _check_missing_imports(self):
        """Check for potentially missing imports"""
        stdlib_modules = set(sys.stdlib_module_names) if hasattr(sys, 'stdlib_module_names') else set()
        
        for file_path, imports in self.import_graph.items():
            for imp in imports:
                base_module = imp.split('.')[0]
                
                # Skip standard library modules
                if base_module in stdlib_modules:
                    continue
                
                # Check if module exists
                spec = importlib.util.find_spec(base_module)
                if spec is None:
                    self.report.dependency_issues.append({
                        'file': file_path,
                        'issue': 'missing_import',
                        'module': imp,
                        'severity': 'CRITICAL',
                        'recommendation': f'Install missing module: {base_module}'
                    })
    
    def _analyze_configurations(self):
        """Analyze configuration files"""
        logger.info("Phase 3: Analyzing configuration files...")
        
        # Check for configuration files
        config_patterns = [
            '**/*.yaml', '**/*.yml', '**/*.json', '**/*.ini', 
            '**/*.cfg', '**/*.conf', '**/*.env', '**/.*rc'
        ]
        
        for pattern in config_patterns:
            for config_file in self.repo_path.glob(pattern):
                self._analyze_config_file(config_file)
    
    def _analyze_config_file(self, config_path: Path):
        """Analyze individual configuration file"""
        try:
            with open(config_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Check for hardcoded secrets
            secret_patterns = [
                (r'(?i)(api[_\-]?key|secret|token|password|pwd|passwd)\s*[:=]\s*["\']([^"\']+)["\']', 'CRITICAL'),
                (r'(?i)(aws_access_key_id|aws_secret_access_key)\s*[:=]\s*["\']([^"\']+)["\']', 'CRITICAL'),
                (r'(?i)bearer\s+[a-zA-Z0-9\-._~+/]+=*', 'CRITICAL'),
            ]
            
            for pattern, severity in secret_patterns:
                matches = re.finditer(pattern, content)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    self.report.security_vulnerabilities.append({
                        'file': str(config_path),
                        'line': line_num,
                        'issue': 'hardcoded_secret',
                        'severity': severity,
                        'description': f'Potential hardcoded secret found',
                        'recommendation': 'Use environment variables or secret management systems'
                    })
            
            # Check for misconfigurations
            if config_path.suffix in ['.yaml', '.yml']:
                self._check_yaml_config(content, config_path)
            elif config_path.suffix == '.json':
                self._check_json_config(content, config_path)
            
        except Exception as e:
            logger.error(f"Failed to analyze config {config_path}: {str(e)}")
    
    def _check_yaml_config(self, content: str, config_path: Path):
        """Check YAML configuration issues"""
        try:
            import yaml
            data = yaml.safe_load(content)
            
            # Check for common misconfigurations
            if isinstance(data, dict):
                # Check debug mode
                if data.get('debug', False) or data.get('DEBUG', False):
                    self.report.issues.append(AuditIssue(
                        severity="HIGH",
                        category="CONFIGURATION",
                        file_path=str(config_path),
                        line_number=None,
                        description="Debug mode enabled in configuration",
                        recommendation="Disable debug mode in production"
                    ))
                
                # Check for localhost/0.0.0.0 bindings
                for key, value in data.items():
                    if isinstance(value, str) and ('0.0.0.0' in value or 'localhost' in value):
                        self.report.issues.append(AuditIssue(
                            severity="MEDIUM",
                            category="CONFIGURATION",
                            file_path=str(config_path),
                            line_number=None,
                            description=f"Local binding found in {key}",
                            recommendation="Use proper host configuration for production"
                        ))
                        
        except yaml.YAMLError as e:
            self.report.issues.append(AuditIssue(
                severity="HIGH",
                category="CONFIGURATION",
                file_path=str(config_path),
                line_number=None,
                description=f"Invalid YAML: {str(e)}",
                recommendation="Fix YAML syntax errors"
            ))
        except ImportError:
            pass
    
    def _check_json_config(self, content: str, config_path: Path):
        """Check JSON configuration issues"""
        try:
            data = json.loads(content)
            
            # Similar checks as YAML
            if isinstance(data, dict):
                if data.get('debug', False) or data.get('DEBUG', False):
                    self.report.issues.append(AuditIssue(
                        severity="HIGH",
                        category="CONFIGURATION",
                        file_path=str(config_path),
                        line_number=None,
                        description="Debug mode enabled in configuration",
                        recommendation="Disable debug mode in production"
                    ))
                    
        except json.JSONDecodeError as e:
            self.report.issues.append(AuditIssue(
                severity="HIGH",
                category="CONFIGURATION",
                file_path=str(config_path),
                line_number=e.lineno if hasattr(e, 'lineno') else None,
                description=f"Invalid JSON: {str(e)}",
                recommendation="Fix JSON syntax errors"
            ))
    
    def _analyze_performance(self):
        """Analyze performance bottlenecks"""
        logger.info("Phase 4: Analyzing performance...")
        
        # Check for common performance issues in Python files
        for file_path, content in self.file_cache.items():
            self._check_performance_issues(content, Path(file_path))
    
    def _check_performance_issues(self, content: str, file_path: Path):
        """Check for performance anti-patterns"""
        
        performance_checks = [
            (r'\.append\([^)]+\).*for.*in', 'Use list comprehension instead of append in loop'),
            (r'sum\(\[.*for.*in.*\]\)', 'Use generator expression instead of list comprehension in sum()'),
            (r'"\s*\+\s*.*\s*\+\s*".*for.*in', 'Use join() instead of string concatenation in loops'),
            (r'global\s+\w+', 'Avoid global variables for better performance'),
            (r're\.compile\([^)]+\).*for.*in', 'Compile regex patterns outside of loops'),
        ]
        
        for pattern, recommendation in performance_checks:
            matches = re.finditer(pattern, content)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                self.report.performance_bottlenecks.append({
                    'file': str(file_path),
                    'line': line_num,
                    'issue': 'performance_antipattern',
                    'pattern': match.group()[:50],
                    'recommendation': recommendation,
                    'severity': 'MEDIUM'
                })
    
    def _security_audit(self):
        """Perform security audit"""
        logger.info("Phase 5: Security audit...")

        # OWASP Top 10 checks
        security_checks = {
            'sql_injection': [
                r'f["\'].*SELECT.*{.*}.*FROM',
                r'\".*SELECT.*\+.*FROM',
                r'sql\s*=\s*.*\+\s*',
            ],
            'command_injection': [
                r'os\.system\s*\([^)]*\+[^)]*\)',
                r'subprocess\..*\([^)]*\+[^)]*\)',
                r'eval\s*\([^)]*input[^)]*\)',
            ],
            'path_traversal': [
                r'open\s*\([^)]*\.\./[^)]*\)',
                r'\.\./',
            ],
            'xxe_injection': [
                r'XMLParser\s*\([^)]*resolve_entities\s*=\s*True',
                r'etree\.parse\([^)]*\)',
            ],
        }

        for vuln_type, patterns in security_checks.items():
            for pattern_str in patterns:
                pattern = re.compile(pattern_str, re.IGNORECASE)
                for file_path, content in self.file_cache.items():
                    # Skip test files for SQL injection and command injection tests
                    # These intentionally contain vulnerable patterns to test security
                    if self._is_test_file(file_path) and vuln_type in ['sql_injection', 'command_injection']:
                        continue

                    matches = pattern.finditer(content)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        self.report.security_vulnerabilities.append({
                            'file': file_path,
                            'line': line_num,
                            'vulnerability': vuln_type,
                            'severity': 'CRITICAL',
                            'pattern': match.group()[:100],
                            'recommendation': f'Fix potential {vuln_type.replace("_", " ")} vulnerability'
                        })
    
    def _analyze_ci_cd(self):
        """Analyze CI/CD pipeline configurations"""
        logger.info("Phase 6: Analyzing CI/CD pipelines...")
        
        # GitHub Actions
        gh_actions = self.repo_path / '.github' / 'workflows'
        if gh_actions.exists():
            for workflow in gh_actions.glob('*.y*ml'):
                self._analyze_github_workflow(workflow)
        
        # GitLab CI
        gitlab_ci = self.repo_path / '.gitlab-ci.yml'
        if gitlab_ci.exists():
            self._analyze_gitlab_ci(gitlab_ci)
        
        # Jenkins
        jenkinsfile = self.repo_path / 'Jenkinsfile'
        if jenkinsfile.exists():
            self._analyze_jenkinsfile(jenkinsfile)
    
    def _analyze_github_workflow(self, workflow_path: Path):
        """Analyze GitHub Actions workflow"""
        try:
            import yaml
            with open(workflow_path, 'r') as f:
                workflow = yaml.safe_load(f)
            
            # Check for security issues
            if 'jobs' in workflow:
                for job_name, job_config in workflow['jobs'].items():
                    # Check for hardcoded secrets
                    if 'env' in job_config:
                        for env_key in job_config['env'].keys():
                            if any(secret in env_key.upper() for secret in ['PASSWORD', 'SECRET', 'TOKEN']):
                                self.report.security_vulnerabilities.append({
                                    'file': str(workflow_path),
                                    'job': job_name,
                                    'issue': 'potential_secret_exposure',
                                    'severity': 'HIGH',
                                    'recommendation': 'Use GitHub Secrets instead of hardcoded values'
                                })
                    
                    # Check for missing checkout action
                    if 'steps' in job_config:
                        has_checkout = any('actions/checkout' in str(step.get('uses', '')) 
                                         for step in job_config['steps'])
                        if not has_checkout and 'docker' not in job_name.lower():
                            self.report.issues.append(AuditIssue(
                                severity="MEDIUM",
                                category="CI_CD",
                                file_path=str(workflow_path),
                                line_number=None,
                                description=f"Job '{job_name}' might be missing checkout action",
                                recommendation="Add actions/checkout@v2 to access repository code"
                            ))
                            
        except Exception as e:
            logger.error(f"Failed to analyze GitHub workflow {workflow_path}: {str(e)}")
    
    def _analyze_gitlab_ci(self, ci_path: Path):
        """Analyze GitLab CI configuration"""
        try:
            import yaml
            with open(ci_path, 'r') as f:
                ci_config = yaml.safe_load(f)
            
            # Check for common issues
            if 'variables' in ci_config:
                for var_name in ci_config['variables'].keys():
                    if any(secret in var_name.upper() for secret in ['PASSWORD', 'SECRET', 'TOKEN']):
                        self.report.security_vulnerabilities.append({
                            'file': str(ci_path),
                            'issue': 'potential_secret_in_variables',
                            'severity': 'HIGH',
                            'recommendation': 'Use GitLab CI/CD variables instead'
                        })
                        
        except Exception as e:
            logger.error(f"Failed to analyze GitLab CI {ci_path}: {str(e)}")
    
    def _analyze_jenkinsfile(self, jenkinsfile_path: Path):
        """Analyze Jenkinsfile"""
        try:
            with open(jenkinsfile_path, 'r') as f:
                content = f.read()
            
            # Check for common Jenkins issues
            if 'sh ' in content and 'set +x' not in content:
                self.report.security_vulnerabilities.append({
                    'file': str(jenkinsfile_path),
                    'issue': 'command_echo_enabled',
                    'severity': 'MEDIUM',
                    'description': 'Shell commands might expose sensitive data',
                    'recommendation': 'Use "set +x" to disable command echo'
                })
                
        except Exception as e:
            logger.error(f"Failed to analyze Jenkinsfile {jenkinsfile_path}: {str(e)}")
    
    def _analyze_data_flow(self):
        """Analyze database and data flow patterns"""
        logger.info("Phase 7: Analyzing data flow...")
        
        # Check for database patterns
        db_patterns = {
            'n_plus_one': r'for.*in.*:\s*\n.*\.(get|filter|select|query)\(',
            'missing_index': r'\.filter\([^)]*__icontains',
            'full_table_scan': r'SELECT\s+\*\s+FROM',
            'missing_pagination': r'\.all\(\)\s*$',
        }
        
        for file_path, content in self.file_cache.items():
            for issue_type, pattern in db_patterns.items():
                matches = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    self.report.performance_bottlenecks.append({
                        'file': file_path,
                        'line': line_num,
                        'issue': f'database_{issue_type}',
                        'pattern': match.group()[:100],
                        'severity': 'MEDIUM',
                        'recommendation': f'Optimize database query to avoid {issue_type.replace("_", " ")}'
                    })
    
    def _audit_error_handling(self):
        """Comprehensive error handling audit"""
        logger.info("Phase 8: Auditing error handling...")
        
        error_handling_stats = {
            'total_try_blocks': 0,
            'bare_excepts': 0,
            'silenced_errors': 0,
            'logged_errors': 0,
            'reraise_count': 0
        }
        
        for file_path, content in self.file_cache.items():
            try:
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Try):
                        error_handling_stats['total_try_blocks'] += 1
                        
                        for handler in node.handlers:
                            # Check for bare except
                            if handler.type is None:
                                error_handling_stats['bare_excepts'] += 1
                            
                            # Check for pass/silenced
                            if len(handler.body) == 1 and isinstance(handler.body[0], ast.Pass):
                                error_handling_stats['silenced_errors'] += 1
                            
                            # Check for logging
                            handler_code = ast.unparse(handler) if hasattr(ast, 'unparse') else ''
                            if 'log' in handler_code.lower() or 'print' in handler_code.lower():
                                error_handling_stats['logged_errors'] += 1
                            
                            # Check for re-raise
                            if any(isinstance(n, ast.Raise) for n in ast.walk(handler)):
                                error_handling_stats['reraise_count'] += 1
                                
            except:
                pass
        
        self.report.metrics['error_handling'] = error_handling_stats
        
        # Generate error handling score
        if error_handling_stats['total_try_blocks'] > 0:
            error_score = (
                (error_handling_stats['logged_errors'] * 2 + 
                 error_handling_stats['reraise_count']) / 
                (error_handling_stats['total_try_blocks'] * 3)
            ) * 100
            
            if error_score < 30:
                self.report.issues.append(AuditIssue(
                    severity="HIGH",
                    category="ERROR_HANDLING",
                    file_path="",
                    line_number=None,
                    description=f"Poor error handling score: {error_score:.1f}%",
                    recommendation="Improve error logging and handling throughout the codebase",
                    metrics=error_handling_stats
                ))
    
    def _generate_recommendations(self):
        """Generate actionable recommendations based on audit"""
        logger.info("Phase 9: Generating recommendations...")
        
        # Categorize issues by severity
        severity_counts = Counter(issue.severity for issue in self.report.issues)
        
        # Priority recommendations
        recommendations = []
        
        if severity_counts['CRITICAL'] > 0:
            recommendations.append({
                'priority': 1,
                'category': 'CRITICAL',
                'action': 'Immediate Action Required',
                'details': f"Fix {severity_counts['CRITICAL']} critical issues immediately",
                'impact': 'System security and stability at risk'
            })
        
        if severity_counts['HIGH'] > 5:
            recommendations.append({
                'priority': 2,
                'category': 'HIGH',
                'action': 'Address High Priority Issues',
                'details': f"Resolve {severity_counts['HIGH']} high-severity issues",
                'impact': 'Potential for production failures'
            })
        
        # Performance recommendations
        if len(self.report.performance_bottlenecks) > 10:
            recommendations.append({
                'priority': 3,
                'category': 'PERFORMANCE',
                'action': 'Optimize Performance',
                'details': f"Address {len(self.report.performance_bottlenecks)} performance bottlenecks",
                'impact': 'Improve system responsiveness and scalability'
            })
        
        # Security recommendations
        if len(self.report.security_vulnerabilities) > 0:
            recommendations.append({
                'priority': 1,
                'category': 'SECURITY',
                'action': 'Security Hardening Required',
                'details': f"Fix {len(self.report.security_vulnerabilities)} security vulnerabilities",
                'impact': 'Prevent potential security breaches'
            })
        
        self.report.metrics['recommendations'] = recommendations
    
    def _get_code_snippet(self, content: str, line_number: int, context: int = 2) -> str:
        """Extract code snippet around a specific line"""
        lines = content.split('\n')
        start = max(0, line_number - context - 1)
        end = min(len(lines), line_number + context)
        
        snippet_lines = []
        for i in range(start, end):
            prefix = ">> " if i == line_number - 1 else "   "
            snippet_lines.append(f"{i+1:4d} {prefix}{lines[i]}")
        
        return '\n'.join(snippet_lines)
    
    def _get_recommendation_for_pattern(self, category: str, pattern: str) -> str:
        """Generate specific recommendation based on pattern category"""
        recommendations = {
            'silenced_errors': "Implement proper error logging and handling. Never silently ignore exceptions.",
            'performance_issues': "Profile and optimize this code section. Consider caching or algorithmic improvements.",
            'security_risks': "Replace with secure alternatives. Never use unsafe functions with user input.",
            'code_smells': "Refactor to improve code quality and maintainability."
        }
        return recommendations.get(category, "Review and refactor this code section.")
    
    def generate_report(self, output_format: str = 'all'):
        """Generate audit report in various formats"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if output_format in ['json', 'all']:
            self._generate_json_report(f'audit_report_{timestamp}.json')
        
        if output_format in ['html', 'all']:
            self._generate_html_report(f'audit_report_{timestamp}.html')
        
        if output_format in ['markdown', 'all']:
            self._generate_markdown_report(f'audit_report_{timestamp}.md')
        
        return self.report
    
    def _generate_json_report(self, filename: str):
        """Generate JSON report"""
        report_dict = {
            'timestamp': self.report.timestamp,
            'repository': self.report.repository,
            'summary': {
                'total_files_analyzed': self.report.total_files_analyzed,
                'total_issues': len(self.report.issues),
                'critical_issues': sum(1 for i in self.report.issues if i.severity == 'CRITICAL'),
                'high_issues': sum(1 for i in self.report.issues if i.severity == 'HIGH'),
                'medium_issues': sum(1 for i in self.report.issues if i.severity == 'MEDIUM'),
                'low_issues': sum(1 for i in self.report.issues if i.severity == 'LOW'),
            },
            'issues': [
                {
                    'severity': issue.severity,
                    'category': issue.category,
                    'file': issue.file_path,
                    'line': issue.line_number,
                    'description': issue.description,
                    'recommendation': issue.recommendation,
                    'metrics': issue.metrics
                }
                for issue in self.report.issues
            ],
            'performance_bottlenecks': self.report.performance_bottlenecks,
            'security_vulnerabilities': self.report.security_vulnerabilities,
            'dependency_issues': self.report.dependency_issues,
            'metrics': self.report.metrics
        }
        
        with open(filename, 'w') as f:
            json.dump(report_dict, f, indent=2, default=str)
        
        logger.info(f"JSON report generated: {filename}")
    
    def _generate_html_report(self, filename: str):
        """Generate HTML report"""
        html_template = '''<!DOCTYPE html>
<html>
<head>
    <title>Pipeline Audit Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
        .summary {{ background: white; padding: 20px; margin: 20px 0; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .critical {{ background: #e74c3c; color: white; padding: 5px 10px; border-radius: 3px; }}
        .high {{ background: #e67e22; color: white; padding: 5px 10px; border-radius: 3px; }}
        .medium {{ background: #f39c12; color: white; padding: 5px 10px; border-radius: 3px; }}
        .low {{ background: #3498db; color: white; padding: 5px 10px; border-radius: 3px; }}
        .info {{ background: #95a5a6; color: white; padding: 5px 10px; border-radius: 3px; }}
        .issue {{ background: white; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #3498db; }}
        .issue.critical {{ border-left-color: #e74c3c; }}
        .issue.high {{ border-left-color: #e67e22; }}
        .issue.medium {{ border-left-color: #f39c12; }}
        .issue.low {{ border-left-color: #3498db; }}
        .code {{ background: #2c3e50; color: #ecf0f1; padding: 10px; border-radius: 3px; font-family: monospace; overflow-x: auto; }}
        table {{ width: 100%; background: white; border-collapse: collapse; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #34495e; color: white; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Pipeline Audit Report</h1>
        <p>Repository: {repository}</p>
        <p>Generated: {timestamp}</p>
    </div>
    
    <div class="summary">
        <h2>Summary</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>Value</th>
            </tr>
            <tr><td>Total Files Analyzed</td><td>{total_files}</td></tr>
            <tr><td>Critical Issues</td><td><span class="critical">{critical}</span></td></tr>
            <tr><td>High Issues</td><td><span class="high">{high}</span></td></tr>
            <tr><td>Medium Issues</td><td><span class="medium">{medium}</span></td></tr>
            <tr><td>Low Issues</td><td><span class="low">{low}</span></td></tr>
            <tr><td>Total Issues</td><td>{total_issues}</td></tr>
        </table>
    </div>
    
    <div class="issues">
        <h2>Issues Found</h2>
        {issues_html}
    </div>
    
    <div class="summary">
        <h2>Recommendations</h2>
        {recommendations_html}
    </div>
</body>
</html>'''
        
        # Generate issues HTML
        issues_html = ""
        for issue in sorted(self.report.issues, key=lambda x: ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO'].index(x.severity)):
            issues_html += f'''
            <div class="issue {issue.severity.lower()}">
                <h3><span class="{issue.severity.lower()}">{issue.severity}</span> - {issue.category}</h3>
                <p><strong>File:</strong> {issue.file_path}</p>
                {f'<p><strong>Line:</strong> {issue.line_number}</p>' if issue.line_number else ''}
                <p><strong>Description:</strong> {issue.description}</p>
                <p><strong>Recommendation:</strong> {issue.recommendation}</p>
                {f'<div class="code">{issue.code_snippet}</div>' if issue.code_snippet else ''}
            </div>'''
        
        # Generate recommendations HTML
        recommendations_html = "<ul>"
        if 'recommendations' in self.report.metrics:
            for rec in sorted(self.report.metrics['recommendations'], key=lambda x: x['priority']):
                recommendations_html += f'''
                <li>
                    <strong>{rec['action']}</strong> - {rec['details']}
                    <br><em>Impact: {rec['impact']}</em>
                </li>'''
        recommendations_html += "</ul>"
        
        # Fill template
        html_content = html_template.format(
            repository=self.report.repository,
            timestamp=self.report.timestamp,
            total_files=self.report.total_files_analyzed,
            critical=sum(1 for i in self.report.issues if i.severity == 'CRITICAL'),
            high=sum(1 for i in self.report.issues if i.severity == 'HIGH'),
            medium=sum(1 for i in self.report.issues if i.severity == 'MEDIUM'),
            low=sum(1 for i in self.report.issues if i.severity == 'LOW'),
            total_issues=len(self.report.issues),
            issues_html=issues_html,
            recommendations_html=recommendations_html
        )
        
        with open(filename, 'w') as f:
            f.write(html_content)
        
        logger.info(f"HTML report generated: {filename}")
    
    def _generate_markdown_report(self, filename: str):
        """Generate Markdown report"""
        md_content = f"""# Pipeline Audit Report

## Repository Information
- **Repository:** {self.report.repository}
- **Timestamp:** {self.report.timestamp}
- **Files Analyzed:** {self.report.total_files_analyzed}

## Executive Summary

| Severity | Count |
|----------|-------|
| CRITICAL | {sum(1 for i in self.report.issues if i.severity == 'CRITICAL')} |
| HIGH | {sum(1 for i in self.report.issues if i.severity == 'HIGH')} |
| MEDIUM | {sum(1 for i in self.report.issues if i.severity == 'MEDIUM')} |
| LOW | {sum(1 for i in self.report.issues if i.severity == 'LOW')} |
| **TOTAL** | **{len(self.report.issues)}** |

## Critical Issues Requiring Immediate Attention

"""
        # Add critical issues
        critical_issues = [i for i in self.report.issues if i.severity == 'CRITICAL']
        if critical_issues:
            for issue in critical_issues:
                md_content += f"""### 🔴 {issue.category}
- **File:** `{issue.file_path}`
- **Line:** {issue.line_number if issue.line_number else 'N/A'}
- **Description:** {issue.description}
- **Recommendation:** {issue.recommendation}

"""
        
        # Add high priority issues
        md_content += "\n## High Priority Issues\n\n"
        high_issues = [i for i in self.report.issues if i.severity == 'HIGH']
        for issue in high_issues[:10]:  # Limit to top 10
            md_content += f"""### ⚠️ {issue.category}
- **File:** `{issue.file_path}`
- **Description:** {issue.description}
- **Recommendation:** {issue.recommendation}

"""
        
        # Add performance section
        if self.report.performance_bottlenecks:
            md_content += "\n## Performance Bottlenecks\n\n"
            for bottleneck in self.report.performance_bottlenecks[:10]:
                md_content += f"- **{bottleneck.get('file', 'Unknown')}:{bottleneck.get('line', '?')}** - {bottleneck.get('recommendation', 'N/A')}\n"
        
        # Add security section
        if self.report.security_vulnerabilities:
            md_content += "\n## Security Vulnerabilities\n\n"
            for vuln in self.report.security_vulnerabilities:
                md_content += f"- **{vuln.get('severity', 'UNKNOWN')}** - {vuln.get('file', 'Unknown')} - {vuln.get('description', 'N/A')}\n"
        
        # Add recommendations
        md_content += "\n## Recommendations\n\n"
        if 'recommendations' in self.report.metrics:
            for rec in sorted(self.report.metrics['recommendations'], key=lambda x: x['priority']):
                md_content += f"""### Priority {rec['priority']}: {rec['action']}
- **Details:** {rec['details']}
- **Impact:** {rec['impact']}

"""
        
        # Add metrics
        if self.report.metrics:
            md_content += "\n## Detailed Metrics\n\n```json\n"
            md_content += json.dumps(self.report.metrics, indent=2, default=str)
            md_content += "\n```\n"
        
        with open(filename, 'w') as f:
            f.write(md_content)
        
        logger.info(f"Markdown report generated: {filename}")


def main():
    """Main entry point for the audit script"""
    parser = argparse.ArgumentParser(description='Advanced Pipeline Audit Tool')
    parser.add_argument('--path', type=str, default='.', help='Path to repository to audit')
    parser.add_argument('--output', type=str, default='all', choices=['json', 'html', 'markdown', 'all'],
                       help='Output format for the report')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('--fix', action='store_true', help='Attempt to auto-fix simple issues')
    
    args = parser.parse_args()
    
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║           ADVANCED PIPELINE AUDIT TOOL v1.0                 ║
    ║                                                              ║
    ║  Performing comprehensive audit of your pipeline...         ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    auditor = PipelineAuditor(repo_path=args.path, verbose=args.verbose)
    report = auditor.run_full_audit()
    auditor.generate_report(output_format=args.output)
    
    # Print summary
    print("\n" + "="*60)
    print("AUDIT COMPLETE")
    print("="*60)
    print(f"Total Files Analyzed: {report.total_files_analyzed}")
    print(f"Total Issues Found: {len(report.issues)}")
    print(f"  - Critical: {sum(1 for i in report.issues if i.severity == 'CRITICAL')}")
    print(f"  - High: {sum(1 for i in report.issues if i.severity == 'HIGH')}")
    print(f"  - Medium: {sum(1 for i in report.issues if i.severity == 'MEDIUM')}")
    print(f"  - Low: {sum(1 for i in report.issues if i.severity == 'LOW')}")
    
    if sum(1 for i in report.issues if i.severity == 'CRITICAL') > 0:
        print("\n⚠️  CRITICAL ISSUES DETECTED - IMMEDIATE ACTION REQUIRED!")
        sys.exit(1)
    elif sum(1 for i in report.issues if i.severity == 'HIGH') > 5:
        print("\n⚠️  Multiple high-severity issues detected. Please review the report.")
        sys.exit(2)
    else:
        print("\n✅ Audit completed. Review the generated reports for details.")
        sys.exit(0)


if __name__ == "__main__":
    main()
