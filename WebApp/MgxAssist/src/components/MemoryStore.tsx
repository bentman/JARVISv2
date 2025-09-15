import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Database, Search, Tag, Clock, Shield, Star, Filter, Plus } from 'lucide-react';
import { memorySnippets, MemorySnippet } from '@/lib/systemData';

interface MemoryStoreProps {
  onSnippetSelect?: (snippet: MemorySnippet) => void;
}

export default function MemoryStore({ onSnippetSelect }: MemoryStoreProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTag, setSelectedTag] = useState<string | null>(null);
  const [selectedAccessLevel, setSelectedAccessLevel] = useState<string | null>(null);
  const [filteredSnippets, setFilteredSnippets] = useState(memorySnippets);

  // Get all unique tags
  const allTags = Array.from(new Set(memorySnippets.flatMap(snippet => snippet.metadata.tags)));
  const accessLevels = ['private', 'shared', 'public'];

  const filterSnippets = () => {
    let filtered = memorySnippets;

    // Search filter
    if (searchQuery) {
      filtered = filtered.filter(snippet => 
        snippet.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
        snippet.metadata.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase())) ||
        snippet.metadata.source.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Tag filter
    if (selectedTag) {
      filtered = filtered.filter(snippet => snippet.metadata.tags.includes(selectedTag));
    }

    // Access level filter
    if (selectedAccessLevel) {
      filtered = filtered.filter(snippet => snippet.metadata.accessLevel === selectedAccessLevel);
    }

    setFilteredSnippets(filtered);
  };

  React.useEffect(() => {
    filterSnippets();
  }, [searchQuery, selectedTag, selectedAccessLevel]);

  const getAccessLevelColor = (level: string) => {
    switch (level) {
      case 'private': return 'bg-red-100 text-red-800';
      case 'shared': return 'bg-yellow-100 text-yellow-800';
      case 'public': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getRelevanceColor = (score: number) => {
    if (score >= 0.9) return 'text-green-600';
    if (score >= 0.7) return 'text-yellow-600';
    return 'text-gray-600';
  };

  const formatTimestamp = (date: Date) => {
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHours / 24);

    if (diffHours < 1) return 'Just now';
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  const clearFilters = () => {
    setSearchQuery('');
    setSelectedTag(null);
    setSelectedAccessLevel(null);
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Database className="h-5 w-5" />
          Memory Store
        </CardTitle>
        <CardDescription>
          Versioned knowledge snippets with search and access controls
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="search" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="search">Search & Browse</TabsTrigger>
            <TabsTrigger value="recent">Recent</TabsTrigger>
            <TabsTrigger value="manage">Manage</TabsTrigger>
          </TabsList>
          
          <TabsContent value="search" className="space-y-4">
            {/* Search and Filters */}
            <div className="space-y-3">
              <div className="flex gap-2">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Search memory snippets..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10"
                  />
                </div>
                <Button variant="outline" size="icon">
                  <Filter className="h-4 w-4" />
                </Button>
              </div>

              {/* Filter Tags */}
              <div className="flex flex-wrap gap-2">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Tag className="h-3 w-3" />
                  Tags:
                </div>
                {allTags.slice(0, 8).map((tag) => (
                  <Badge
                    key={tag}
                    variant={selectedTag === tag ? "default" : "outline"}
                    className="cursor-pointer"
                    onClick={() => setSelectedTag(selectedTag === tag ? null : tag)}
                  >
                    {tag}
                  </Badge>
                ))}
              </div>

              {/* Access Level Filter */}
              <div className="flex flex-wrap gap-2">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Shield className="h-3 w-3" />
                  Access:
                </div>
                {accessLevels.map((level) => (
                  <Badge
                    key={level}
                    variant={selectedAccessLevel === level ? "default" : "outline"}
                    className={`cursor-pointer ${selectedAccessLevel === level ? '' : getAccessLevelColor(level)}`}
                    onClick={() => setSelectedAccessLevel(selectedAccessLevel === level ? null : level)}
                  >
                    {level}
                  </Badge>
                ))}
                {(selectedTag || selectedAccessLevel || searchQuery) && (
                  <Button variant="ghost" size="sm" onClick={clearFilters}>
                    Clear filters
                  </Button>
                )}
              </div>
            </div>

            {/* Search Results */}
            <div className="space-y-3">
              {filteredSnippets.length === 0 ? (
                <Card className="p-6 text-center">
                  <div className="text-muted-foreground">
                    No memory snippets found matching your criteria.
                  </div>
                </Card>
              ) : (
                filteredSnippets.map((snippet) => (
                  <SnippetCard
                    key={snippet.id}
                    snippet={snippet}
                    onSelect={() => onSnippetSelect?.(snippet)}
                  />
                ))
              )}
            </div>
          </TabsContent>
          
          <TabsContent value="recent" className="space-y-4">
            <div className="space-y-3">
              {memorySnippets
                .sort((a, b) => b.metadata.timestamp.getTime() - a.metadata.timestamp.getTime())
                .slice(0, 10)
                .map((snippet) => (
                  <SnippetCard
                    key={snippet.id}
                    snippet={snippet}
                    onSelect={() => onSnippetSelect?.(snippet)}
                    showTimestamp={true}
                  />
                ))}
            </div>
          </TabsContent>
          
          <TabsContent value="manage" className="space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold">Memory Management</h3>
              <Button className="gap-2">
                <Plus className="h-4 w-4" />
                Add Snippet
              </Button>
            </div>

            {/* Statistics */}
            <div className="grid grid-cols-3 gap-4">
              <Card className="p-4">
                <div className="text-2xl font-bold text-blue-600">{memorySnippets.length}</div>
                <div className="text-sm text-muted-foreground">Total Snippets</div>
              </Card>
              <Card className="p-4">
                <div className="text-2xl font-bold text-green-600">{allTags.length}</div>
                <div className="text-sm text-muted-foreground">Unique Tags</div>
              </Card>
              <Card className="p-4">
                <div className="text-2xl font-bold text-purple-600">
                  {Math.round(memorySnippets.reduce((sum, s) => sum + s.relevanceScore, 0) / memorySnippets.length * 100)}%
                </div>
                <div className="text-sm text-muted-foreground">Avg. Relevance</div>
              </Card>
            </div>

            {/* Storage Usage */}
            <Card className="p-4">
              <h4 className="font-medium mb-3">Storage Usage</h4>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Used: 2.3 MB</span>
                  <span>Limit: 100 MB</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-blue-600 h-2 rounded-full" style={{ width: '2.3%' }}></div>
                </div>
              </div>
            </Card>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}

interface SnippetCardProps {
  snippet: MemorySnippet;
  onSelect: () => void;
  showTimestamp?: boolean;
}

function SnippetCard({ snippet, onSelect, showTimestamp = false }: SnippetCardProps) {
  const getAccessLevelColor = (level: string) => {
    switch (level) {
      case 'private': return 'bg-red-100 text-red-800';
      case 'shared': return 'bg-yellow-100 text-yellow-800';
      case 'public': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getRelevanceColor = (score: number) => {
    if (score >= 0.9) return 'text-green-600';
    if (score >= 0.7) return 'text-yellow-600';
    return 'text-gray-600';
  };

  const formatTimestamp = (date: Date) => {
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHours / 24);

    if (diffHours < 1) return 'Just now';
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  return (
    <Card className="cursor-pointer hover:shadow-md transition-all" onClick={onSelect}>
      <CardContent className="p-4">
        <div className="flex items-start justify-between mb-2">
          <div className="flex items-center gap-2">
            <Badge className={getAccessLevelColor(snippet.metadata.accessLevel)}>
              {snippet.metadata.accessLevel}
            </Badge>
            <Badge variant="outline">v{snippet.metadata.version}</Badge>
            {showTimestamp && (
              <div className="flex items-center gap-1 text-xs text-muted-foreground">
                <Clock className="h-3 w-3" />
                {formatTimestamp(snippet.metadata.timestamp)}
              </div>
            )}
          </div>
          <div className="flex items-center gap-1">
            <Star className={`h-4 w-4 ${getRelevanceColor(snippet.relevanceScore)}`} />
            <span className={`text-sm font-medium ${getRelevanceColor(snippet.relevanceScore)}`}>
              {Math.round(snippet.relevanceScore * 100)}%
            </span>
          </div>
        </div>
        
        <p className="text-sm mb-3 line-clamp-2">{snippet.content}</p>
        
        <div className="flex items-center justify-between">
          <div className="flex flex-wrap gap-1">
            {snippet.metadata.tags.slice(0, 3).map((tag) => (
              <Badge key={tag} variant="secondary" className="text-xs">
                {tag}
              </Badge>
            ))}
            {snippet.metadata.tags.length > 3 && (
              <Badge variant="secondary" className="text-xs">
                +{snippet.metadata.tags.length - 3}
              </Badge>
            )}
          </div>
          <div className="text-xs text-muted-foreground">
            {snippet.metadata.source}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}