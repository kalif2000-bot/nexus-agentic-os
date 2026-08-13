import React, { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import {
  ArrowUpRight,
  Award,
  BriefcaseBusiness,
  Cloud,
  Code2,
  Database,
  Download,
  Github,
  Linkedin,
  Mail,
  Menu,
  Network,
  Phone,
  ServerCog,
  ShieldCheck,
  Terminal,
  X
} from 'lucide-react';
import './styles.css';

const profile = {
  name: 'Kalifullah Dhameem Ansari',
  title: 'Site Reliability Engineer | DevOps & Platform Engineer',
  tagline: 'Building reliable cloud platforms, automating infrastructure, and scaling production systems.',
  email: 'kalians2000@gmail.com',
  phone: '+91 85500 87921',
  github: 'https://github.com/kalif2000-bot',
  linkedin: 'https://www.linkedin.com/in/kalif2000',
  resume: '/Kalifullah-Dhameem-Ansari-Resume.pdf'
};

const navItems = ['About', 'Skills', 'Experience', 'Project', 'Certifications', 'GitHub', 'Contact'];

const skillGroups = [
  { title: 'Cloud', icon: Cloud, items: ['Azure', 'AWS'] },
  { title: 'Containers & Orchestration', icon: ServerCog, items: ['AKS', 'Kubernetes', 'Docker', 'Helm'] },
  { title: 'DevOps & Automation', icon: Terminal, items: ['Terraform', 'Ansible', 'Azure DevOps', 'Jenkins', 'GitHub Actions', 'CI/CD', 'IaC'] },
  { title: 'Monitoring', icon: Network, items: ['Datadog', 'Prometheus', 'Grafana', 'ELK', 'Azure Monitor'] },
  { title: 'Programming', icon: Code2, items: ['Python', 'Bash', 'Java'] },
  { title: 'Databases & Messaging', icon: Database, items: ['PostgreSQL', 'Redis', 'Kafka', 'Azure Event Hub'] },
  { title: 'Security & Reliability', icon: ShieldCheck, items: ['Azure Key Vault', 'RBAC', 'Workload Identity', 'RCA', 'SLO/SLI', 'Microservices'] }
];

const experiences = [
  {
    company: 'Harman International',
    context: 'Client: Mercedes-Benz',
    role: 'Site Reliability Engineer',
    period: 'Jan 2026 - Aug 2026',
    bullets: [
      'Managed production Azure Kubernetes Service clusters supporting Mercedes-Benz Personalization services across EMEA, AMAP, and China regions.',
      'Automated AKS, PostgreSQL, Redis, Azure Event Hub, and Azure Key Vault provisioning with reusable Terraform modules.',
      'Optimized Azure DevOps CI/CD pipelines with Helm-based Kubernetes deployment strategies to improve release reliability.',
      'Built Datadog dashboards, monitors, and SLO-based alerting while driving Kubernetes diagnostics, RCA, and MTTR improvements.'
    ]
  },
  {
    company: 'Exotel',
    context: 'Communications platform',
    role: 'Site Reliability Engineer',
    period: 'Jul 2025 - Jan 2026',
    bullets: [
      'Maintained Jenkins pipelines and infrastructure automation using Terraform, Ansible, Docker, and Kubernetes.',
      'Supported Linux production environments with a focus on availability, release reliability, and operational clarity.',
      'Improved proactive alerting, performance optimization, and observability with Prometheus, Grafana, and ELK.'
    ]
  },
  {
    company: 'HCL Technologies',
    context: 'Enterprise cloud delivery',
    role: 'Azure DevOps Engineer',
    period: 'Sep 2022 - Jun 2025',
    bullets: [
      'Implemented CI/CD workflows across Azure DevOps, Jenkins, and GitHub Actions for application and platform teams.',
      'Worked on AKS, Helm, Azure Monitor, Python, and Bash automation to simplify repeatable engineering operations.',
      'Managed Docker and AKS deployments with reusable IaC modules across multiple enterprise environments.'
    ]
  }
];

const certifications = [
  'Microsoft Azure AZ-900',
  'Microsoft Azure AZ-104',
  'AWS SysOps Administrator',
  'ACS Skills Assessment',
  'CKA (In Progress)'
];

const fallbackRepos = [
  {
    name: 'azure-devops-automation',
    description: 'Infrastructure automation patterns for Azure DevOps, Terraform, AKS, and release pipelines.',
    language: 'Terraform'
  },
  {
    name: 'kubernetes-observability',
    description: 'Prometheus, Grafana, and Kubernetes monitoring examples for production reliability workflows.',
    language: 'Shell'
  },
  {
    name: 'sre-platform-toolkit',
    description: 'Reusable scripts and operational checklists for Linux, Docker, CI/CD, and incident response.',
    language: 'Python'
  }
];

function App() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [repos, setRepos] = useState(fallbackRepos);

  useEffect(() => {
    fetch('https://api.github.com/users/kalif2000-bot/repos?sort=updated&per_page=6')
      .then((response) => (response.ok ? response.json() : Promise.reject(new Error('GitHub API unavailable'))))
      .then((data) => {
        const visibleRepos = data
          .filter((repo) => !repo.fork)
          .slice(0, 6)
          .map((repo) => ({
            name: repo.name,
            description: repo.description || 'Repository by Kalifullah Dhameem Ansari.',
            language: repo.language || 'DevOps',
            html_url: repo.html_url,
            topics: repo.topics || []
          }));

        if (visibleRepos.length > 0) {
          setRepos(visibleRepos);
        }
      })
      .catch(() => setRepos(fallbackRepos));
  }, []);

  const navLinks = useMemo(
    () =>
      navItems.map((item) => (
        <a key={item} href={`#${item.toLowerCase()}`} onClick={() => setMenuOpen(false)}>
          {item}
        </a>
      )),
    []
  );

  return (
    <>
      <header className="site-header">
        <a className="brand" href="#home" aria-label="Kalifullah home">
          <span>KDA</span>
        </a>
        <nav className={menuOpen ? 'nav-links is-open' : 'nav-links'} aria-label="Primary navigation">
          {navLinks}
        </nav>
        <button className="icon-button nav-toggle" type="button" onClick={() => setMenuOpen((open) => !open)} aria-label="Toggle navigation">
          {menuOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
      </header>

      <main>
        <section className="hero section" id="home">
          <div className="hero-bg" aria-hidden="true" />
          <div className="hero-content">
            <p className="eyebrow">SRE • DevOps • Cloud Platform Engineering</p>
            <h1>{profile.name}</h1>
            <p className="hero-title">{profile.title}</p>
            <p className="hero-tagline">{profile.tagline}</p>
            <div className="hero-actions">
              <a className="button primary" href={profile.resume} download>
                <Download size={18} /> Download Resume
              </a>
              <a className="button" href={profile.github} target="_blank" rel="noreferrer">
                <Github size={18} /> View GitHub
              </a>
              <a className="button" href={profile.linkedin} target="_blank" rel="noreferrer">
                <Linkedin size={18} /> Connect on LinkedIn
              </a>
              <a className="button" href="#contact">
                <Mail size={18} /> Contact Me
              </a>
            </div>
            <div className="signal-row" aria-label="Experience highlights">
              <span>4+ years experience</span>
              <span>Azure & AWS</span>
              <span>AKS, Terraform, CI/CD</span>
              <span>Production reliability</span>
            </div>
          </div>
        </section>

        <section className="section" id="about">
          <div className="section-grid">
            <div>
              <p className="eyebrow">About</p>
              <h2>Reliability engineer for cloud platforms that need to stay boring in production.</h2>
            </div>
            <div className="prose">
              <p>
                I am a Site Reliability Engineer and DevOps Platform Engineer with 4+ years of experience building,
                automating, monitoring, and supporting production systems across Azure and AWS. My work spans Azure
                Kubernetes Service, Kubernetes, Docker, Terraform, Helm, Azure DevOps, Jenkins, GitHub Actions, Linux,
                Python, Datadog, Prometheus, Grafana, PostgreSQL, Redis, Kafka, Azure Event Hub, and practical
                Infrastructure as Code.
              </p>
              <p>
                I focus on platform reliability, CI/CD quality, incident management, production support, observability,
                root cause analysis, SLO/SLI practices, and automation that helps engineering teams release with
                confidence. Recruiters and hiring managers can quickly see a hands-on SRE profile with cloud
                infrastructure depth, Kubernetes operations experience, and a strong bias toward stable production
                outcomes.
              </p>
            </div>
          </div>
        </section>

        <section className="section muted" id="skills">
          <div className="section-heading">
            <p className="eyebrow">Technical Skills</p>
            <h2>Tooling depth across cloud, containers, automation, observability, and production support.</h2>
          </div>
          <div className="skills-grid">
            {skillGroups.map(({ title, icon: Icon, items }) => (
              <article className="skill-card" key={title}>
                <div className="card-heading">
                  <Icon size={22} />
                  <h3>{title}</h3>
                </div>
                <div className="tags">
                  {items.map((item) => (
                    <span key={item}>{item}</span>
                  ))}
                </div>
              </article>
            ))}
          </div>
        </section>

        <section className="section" id="experience">
          <div className="section-heading">
            <p className="eyebrow">Professional Experience</p>
            <h2>Production-first engineering across enterprise platforms and high-availability services.</h2>
          </div>
          <div className="timeline">
            {experiences.map((job) => (
              <article className="timeline-item" key={`${job.company}-${job.period}`}>
                <div className="timeline-meta">
                  <BriefcaseBusiness size={22} />
                  <span>{job.period}</span>
                </div>
                <div className="timeline-body">
                  <div>
                    <h3>{job.company}</h3>
                    <p>{job.context}</p>
                  </div>
                  <strong>{job.role}</strong>
                  <ul>
                    {job.bullets.map((bullet) => (
                      <li key={bullet}>{bullet}</li>
                    ))}
                  </ul>
                </div>
              </article>
            ))}
          </div>
        </section>

        <section className="section project-band" id="project">
          <div className="project-copy">
            <p className="eyebrow">Featured Project</p>
            <h2>Mercedes-Benz Personalization Platform</h2>
            <p>
              Enterprise-scale cloud platform supporting personalization capabilities across EMEA, AMAP, and China
              regions, with a strong emphasis on high availability, platform reliability, production support, and
              incident management.
            </p>
          </div>
          <div className="project-details">
            {['Azure AKS', 'Terraform', 'Helm', 'Azure DevOps', 'Datadog', 'PostgreSQL', 'Redis', 'Azure Event Hub'].map((item) => (
              <span key={item}>{item}</span>
            ))}
          </div>
        </section>

        <section className="section" id="certifications">
          <div className="section-heading">
            <p className="eyebrow">Certifications</p>
            <h2>Credential signals for cloud, operations, and Kubernetes growth.</h2>
          </div>
          <div className="cert-grid">
            {certifications.map((cert) => (
              <article className="cert-card" key={cert}>
                <Award size={22} />
                <span>{cert}</span>
              </article>
            ))}
          </div>
        </section>

        <section className="section resume-band" id="resume">
          <div>
            <p className="eyebrow">Resume</p>
            <h2>Recruiter-ready PDF for SRE and DevOps roles.</h2>
          </div>
          <a className="button primary" href={profile.resume} download>
            <Download size={18} /> Download Resume
          </a>
        </section>

        <section className="section muted" id="github">
          <div className="section-heading">
            <p className="eyebrow">GitHub Projects</p>
            <h2>Recent repositories and platform engineering work from GitHub.</h2>
          </div>
          <div className="repo-grid">
            {repos.map((repo) => (
              <article className="repo-card" key={repo.name}>
                <div className="repo-top">
                  <Github size={21} />
                  <a href={repo.html_url || profile.github} target="_blank" rel="noreferrer" aria-label={`Open ${repo.name} on GitHub`}>
                    <ArrowUpRight size={19} />
                  </a>
                </div>
                <h3>{repo.name}</h3>
                <p>{repo.description}</p>
                <div className="tags compact">
                  <span>{repo.language}</span>
                  {(repo.topics || []).slice(0, 2).map((topic) => (
                    <span key={topic}>{topic}</span>
                  ))}
                </div>
              </article>
            ))}
          </div>
        </section>

        <section className="section contact-section" id="contact">
          <div>
            <p className="eyebrow">Contact</p>
            <h2>Open to SRE, DevOps, and Platform Engineering opportunities.</h2>
            <div className="contact-links">
              <a href={`mailto:${profile.email}`}><Mail size={18} /> {profile.email}</a>
              <a href={`tel:${profile.phone.replace(/\s/g, '')}`}><Phone size={18} /> {profile.phone}</a>
              <a href={profile.linkedin} target="_blank" rel="noreferrer"><Linkedin size={18} /> LinkedIn</a>
              <a href={profile.github} target="_blank" rel="noreferrer"><Github size={18} /> GitHub</a>
            </div>
          </div>
          <form className="contact-form" action={`https://formsubmit.co/${profile.email}`} method="POST">
            <input type="hidden" name="_subject" value="Portfolio contact for Kalifullah Dhameem Ansari" />
            <input type="hidden" name="_captcha" value="false" />
            <label>
              Name
              <input name="name" type="text" required autoComplete="name" />
            </label>
            <label>
              Email
              <input name="email" type="email" required autoComplete="email" />
            </label>
            <label>
              Message
              <textarea name="message" rows="5" required />
            </label>
            <button className="button primary" type="submit">
              <Mail size={18} /> Send Message
            </button>
            <a className="mailto-fallback" href={`mailto:${profile.email}?subject=Portfolio%20contact`}>
              Use email instead
            </a>
          </form>
        </section>
      </main>
    </>
  );
}

createRoot(document.getElementById('root')).render(<App />);
